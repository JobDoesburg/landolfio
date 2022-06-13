function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function sync_database_button_click(button) {
  const HOOK_LOCATION = "/api/accounting/hooks/sync_database";
  const STATUS_AVAILABLE = "\u{1F501} Met MoneyBird synchroniseren";
  const STATUS_BUSY = "\u{23F3} Aan het synchroniseren met MoneyBird";
  const STATUS_FAILED = "\u{274E} Synchroniseren mislukt";
  const STATUS_SUCCESS = "\u{2705} Synchroniseren gelukt";

  button.disabled = true;
  button.innerText = STATUS_BUSY;

  try {
    const response = await fetch(HOOK_LOCATION);

    if (!response.ok) {
      throw "Response was not OK.";
    }

    button.innerText = STATUS_SUCCESS;
    window.location.reload();
  } catch {
    button.innerText = STATUS_FAILED;
    await sleep(3000);
    button.disabled = false;
    button.innerText = STATUS_AVAILABLE;
  }
}
