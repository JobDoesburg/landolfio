from accounting.moneybird.synchronization import synchronize


def sync_moneybird(full_sync=False) -> None:
    synchronize(full_sync=full_sync)
