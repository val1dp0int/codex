"""A Codex database event emitter for use by the observer."""
import os

from logging import getLogger
from pathlib import Path
from threading import Condition

from django.db.models.functions import Now
from django.utils import timezone
from watchdog.events import (
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
)
from watchdog.observers.api import EventEmitter
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

from codex.models import Comic, Folder, Library


LOG = getLogger(__name__)


class CodexDatabaseSnapshot(DirectorySnapshot):
    """Take snapshots from the Codex database."""

    MODELS = (Folder, Comic)

    @classmethod
    def _walk(cls, root):
        """Populate the DirectorySnapshot structures from the database."""
        for model in cls.MODELS:
            yield model.objects.filter(library__path=root).values("path", "stat")

    def _fix_bad_db_stat(self, wp_path, params, stat):
        """Handle null or zeroed out database stat entries."""
        if params and len(params) == 10 and params[1]:
            # params[1] is st_inode, if it's okay most everything else works
            return params
        if Path(wp_path).exists():
            LOG.debug(f"Force modify path with bad db record: {wp_path}")
            params = list(stat(wp_path))
            # Fake mtime will trigger a modified event
            params[8] = 0.0
        else:
            LOG.debug(f"Force delete path with bad db record: {wp_path}")
            # This will trigger a deleted event
            params = Comic.ZERO_STAT
        return params

    def __init__(
        self,
        path,
        _recursive=True,
        walker_callback=(lambda _p, _s: None),
        stat=os.stat,
        listdir=os.listdir,
        force=False,
    ):
        """Initialize like DirectorySnapshot but use a database walk."""
        self._stat_info = {}
        self._inode_to_path = {}
        if not Path(path).is_dir():
            LOG.warning(f"{path} not found, cannot snapshot.")
            return

        # Add the library root
        st = stat(path)
        self._stat_info[path] = st
        self._inode_to_path[(st.st_ino, st.st_dev)] = path

        for queryset in self._walk(path):
            for wp in queryset:
                wp_path = wp["path"]
                params = self._fix_bad_db_stat(wp_path, wp.get("stat"), stat)
                if force:
                    # Fake mtime will trigger modified event
                    params[8] = 0
                st = os.stat_result(params)
                self._inode_to_path[st] = wp_path
                self._stat_info[wp_path] = st
                walker_callback(wp_path, st)


class DatabasePollingEmitter(EventEmitter):
    """Use DatabaseSnapshots to compare against the DirectorySnapshots."""

    DIR_NOT_FOUND_TIMEOUT = 15 * 60

    def __init__(
        self,
        event_queue,
        watch,
        timeout=None,
        stat=os.stat,
        listdir=os.listdir,
    ):
        """Initialize snapshot methods."""
        self._poll_cond = Condition()
        self._force = False
        super().__init__(event_queue, watch)

        self._take_dir_snapshot = lambda: DirectorySnapshot(
            self.watch.path, self.watch.is_recursive, stat=stat, listdir=listdir
        )

    def poll(self, force=False):
        """Poll now, sooner than timeout."""
        if force:
            self._force = True
        with self._poll_cond:
            self._poll_cond.notify()

    def _take_db_snapshot(self):
        """Get a database snapshot with optional force argument."""
        db_snapshot = CodexDatabaseSnapshot(
            self.watch.path, self.watch.is_recursive, force=self._force
        )
        self._force = False
        return db_snapshot

    @property
    def timeout(self):
        library = Library.objects.get(path=self.watch.path)
        if not library.poll:
            LOG.warning(f"Library {self.watch.path} not poll enabled.")
            self._stopped_event.set()
            return 0
        if not Path(self.watch.path).is_dir():
            LOG.warning(f"Library {self.watch.path} not found.")
            return self.DIR_NOT_FOUND_TIMEOUT

        since_last_poll = timezone.now() - library.last_poll
        timeout = max(
            0, library.poll_every.total_seconds() - since_last_poll.total_seconds()
        )
        return timeout

    def queue_events(self, timeout=None):
        """Queue events like PollingEmitter but always use a fresh db snapshot."""
        # We don't want to hit the disk continuously.
        # timeout behaves like an interval for polling emitters.
        with self._poll_cond:
            LOG.verbose(f"Polling {self.watch.path} again in {int(timeout)} seconds.")
            self._poll_cond.wait(timeout)
            if not self.should_keep_running():
                return

            LOG.verbose(f"Polling {self.watch.path}...")
            if not Path(self.watch.path).is_dir():
                LOG.warning(f"{self.watch.path} not found. Not polling.")
                return

            # Get event diff between database snapshot and directory snapshot.
            # Update snapshot.
            db_snapshot = self._take_db_snapshot()
            dir_snapshot = self._take_dir_snapshot()
            events = DirectorySnapshotDiff(db_snapshot, dir_snapshot)
            LOG.debug(events)

            # Files.
            # Could remove non-comics here, but handled by the EventHandler
            for src_path in events.files_deleted:
                self.queue_event(FileDeletedEvent(src_path))
            for src_path in events.files_modified:
                self.queue_event(FileModifiedEvent(src_path))
            for src_path in events.files_created:
                self.queue_event(FileCreatedEvent(src_path))
            for src_path, dest_path in events.files_moved:
                self.queue_event(FileMovedEvent(src_path, dest_path))

            # Directories.
            for src_path in events.dirs_deleted:
                self.queue_event(DirDeletedEvent(src_path))
            for src_path in events.dirs_modified:
                self.queue_event(DirModifiedEvent(src_path))
            # Folders are only created by comics themselves
            # The event handler excludes these but skip it here too.
            # for src_path in events.dirs_created:
            #    self.queue_event(DirCreatedEvent(src_path))
            #
            for src_path, dest_path in events.dirs_moved:
                self.queue_event(DirMovedEvent(src_path, dest_path))

            Library.objects.filter(path=self.watch.path).update(
                last_poll=Now(), updated_at=Now()
            )
        LOG.verbose(f"Poll {self.watch.path} finished.")

    def on_thread_stop(self):
        """Send the poller as well."""
        with self._poll_cond:
            self._poll_cond.notify()