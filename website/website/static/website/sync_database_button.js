function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function sync_database_button_click(button) {
  const HOOK_LOCATION = "/api/accounting/hooks/sync_database";
  const STATUS_AVAILABLE = "\u{1F501} Synchronize with MoneyBird";
  const STATUS_BUSY = "\u{23F3} Synchronizing with MoneyBird";
  const STATUS_FAILED = "\u{274E} Failed to Synchronize";
  const STATUS_SUCCESS = "\u{2705} Successfully Synchronized";

  button.disabled = true;
  button.innerText = STATUS_BUSY;

  try {
    const response = await fetch(HOOK_LOCATION);

    if (!response.ok) {
      throw "Response was not OK.";
    }

    button.innerText = STATUS_SUCCESS;
    await sleep(1000);
    window.location.reload();
  } catch {
    button.innerText = STATUS_FAILED;
    await sleep(3000);
    button.disabled = false;
    button.innerText = STATUS_AVAILABLE;
  }
}
