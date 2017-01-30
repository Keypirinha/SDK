# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import random
import string
import time

MAX_TESTERS = 100
DEFAULT_ENABLED = False
DEFAULT_TESTERS_COUNT = 1
DEFAULT_CATALOG_SIZE = 100000
DEFAULT_CATALOG_BATCH_LEN = 0
DEFAULT_SALT_ITEMS = False

class StressTest(kp.Plugin):
    """
    Stress test of Keypirinha's Catalog for insertion speed, memory usage and
    search speed.
    """
    tester_id = 1
    enabled = DEFAULT_ENABLED
    catalog_size = DEFAULT_CATALOG_SIZE
    catalog_batch_size = DEFAULT_CATALOG_BATCH_LEN
    salt = DEFAULT_SALT_ITEMS

    def __init__(self):
        super().__init__()
        if self.tester_id == 1:
            self._debug = True

    def on_start(self):
        if self.tester_id == 1:
            self.dbg("ON_START")
        self._read_config()

    def on_catalog(self):
        if self.tester_id == 1:
            self.dbg("ON_CATALOG")
        if not self.enabled:
            return

        begin_time = time.monotonic()
        catalog = []
        items_committed = 0
        batches_committed = 0

        if (self.catalog_batch_size > 0 and
                self.catalog_batch_size < self.catalog_size):
            self.set_catalog([])

        for idx in range(1, self.catalog_size + 1):
            if idx % 100:
                if self.should_terminate():
                    self.info("ABORTING ON_CATALOG")
                    return

            item_idstr = "{}.{}".format(self.tester_id, idx)
            item_salt = ""
            if self.salt:
                item_salt = " (salt: " + "".join(
                    random.choice(string.ascii_uppercase) for i in range(5)) + ")"

            catalog.append(self.create_item(
                category=kp.ItemCategory.USER_BASE + 1,
                label="StressTest #{}{}".format(item_idstr, item_salt),
                short_desc="StressTest item from tester #{}{}".format(self.tester_id, item_salt),
                target=item_idstr,
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.IGNORE))

            if self.catalog_batch_size > 0 and len(catalog) % self.catalog_batch_size == 0:
                self.merge_catalog(catalog)
                items_committed += len(catalog)
                batches_committed += 1
                catalog = []

        if catalog:
            if not items_committed:
                self.set_catalog(catalog)
            else:
                self.merge_catalog(catalog)
            items_committed += len(catalog)
            batches_committed += 1
        end_time = time.monotonic()

        self.info("Tester #{} committed {} items ({} batches) in {:.1f} seconds".format(
            self.tester_id, items_committed, batches_committed, end_time - begin_time))

    def on_suggest(self, user_input, items_chain):
        if self.tester_id == 1:
            self.dbg("ON_SUGGEST (\"{}\", #{})".format(user_input, len(items_chain)))
        if not self.enabled: return

    def on_execute(self, item, action):
        if self.tester_id == 1:
            self.dbg("ON_EXECUTE")
        if not self.enabled: return

    def on_activated(self):
        if self.tester_id == 1:
            self.dbg("ON_ACTIVATED")
        if not self.enabled: return

    def on_deactivated(self):
        if self.tester_id == 1:
            self.dbg("ON_DEACTIVATED")
        if not self.enabled: return

    def on_events(self, flags):
        if self.tester_id == 1:
            self.dbg("ON_EVENT ({:#x})".format(flags))
        if flags & kp.Events.PACKCONFIG:
            self._read_config()
            self.on_catalog()

    def _read_config(self):
        settings = self.load_settings()

        was_enabled = self.enabled
        global_enabled = settings.get_bool("enable", "main", DEFAULT_ENABLED)
        self.enabled = global_enabled

        testers_count = settings.get_int(
            "testers", "main", DEFAULT_TESTERS_COUNT, min=1, max=MAX_TESTERS)
        if self.tester_id > testers_count:
            self.enabled = False

        for section in ("tester", "tester/{}".format(self.tester_id)):
            if section != "tester" and not settings.has_section(section):
                # the section != "tester" test allows us to load default values
                # even if the [tester] section is not declared in the config
                # file
                continue

            if global_enabled and self.tester_id <= testers_count:
                self.enabled = settings.get_bool(
                    "enable", section, self.enabled)

            self.catalog_size = settings.get_int(
                "catalog_size", section,
                DEFAULT_CATALOG_SIZE, min=0, max=1000000)
            self.catalog_batch_size = settings.get_int(
                "catalog_batch_size", section,
                DEFAULT_CATALOG_BATCH_LEN)
            self.salt = settings.get_bool(
                "salt", section, DEFAULT_SALT_ITEMS)

        if not self.enabled and was_enabled:
            self.set_catalog([])
            return


def _declare_plugins(package_name):
    """Create plugin classes on-the-fly according to user's configuration :)"""
    classes = [StressTest]
    for tester_id in range(2, MAX_TESTERS + 1):
        class_name = "{}{}".format(package_name, tester_id)
        class_obj = type(class_name, (StressTest,), {'tester_id': tester_id})
        classes.append(class_obj)
    return classes

__keypirinha_plugins__ = _declare_plugins
