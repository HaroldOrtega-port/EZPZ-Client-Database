document.querySelectorAll('[data-add]').forEach(button => {
  button.addEventListener('click', () => {
    const type = button.dataset.add;
    document.querySelector(`#${type === 'contact' ? 'contacts' : 'team'}`).append(document.querySelector(`#${type}-template`).content.cloneNode(true));
  });
});
document.addEventListener('click', event => {
  const remove = event.target.closest('.remove-row');
  if (remove) remove.closest('.person-row').remove();
  const dayButton = event.target.closest('.day-option');
  if (dayButton) {
    dayButton.classList.toggle('selected');
    dayButton.setAttribute('aria-pressed', dayButton.classList.contains('selected') ? 'true' : 'false');
    const picker = dayButton.closest('.day-picker');
    picker.querySelector('input[type="hidden"]').value = [...picker.querySelectorAll('.day-option.selected')].map(button => button.dataset.day).join(',');
  }
});
document.querySelectorAll('.repeat-list').forEach(list => {
  if (!list.children.length) document.querySelector(`[data-add="${list.id === 'contacts' ? 'contact' : 'team'}"]`).click();
});

const scheduleRadios = document.querySelectorAll('input[name="schedule_mode"]');
function updateScheduleMode() {
  const individual = document.querySelector('input[name="schedule_mode"]:checked')?.value === 'individual';
  document.querySelector('#shared-schedule')?.classList.toggle('is-hidden', individual);
  document.querySelectorAll('.member-schedule, .individual-schedule-heading').forEach(element => element.classList.toggle('is-hidden', !individual));
}
scheduleRadios.forEach(radio => radio.addEventListener('change', updateScheduleMode));
updateScheduleMode();

const tableSearch = document.querySelector('#client-table-search');
if (tableSearch) {
  const rows = [...document.querySelectorAll('.client-table-row')];
  const count = document.querySelector('#table-result-count');
  const noResults = document.querySelector('#table-no-results');
  const filterTable = () => {
    const terms = tableSearch.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach(row => {
      const searchableText = row.textContent.toLocaleLowerCase();
      const match = terms.every(term => searchableText.includes(term));
      row.hidden = !match;
      if (match) visible += 1;
    });
    count.textContent = `${visible} ${visible === 1 ? 'client' : 'clients'} shown`;
    noResults.hidden = visible !== 0;
  };
  tableSearch.addEventListener('input', filterTable);
  document.querySelector('#clear-table-search').addEventListener('click', () => { tableSearch.value = ''; filterTable(); tableSearch.focus(); });
  filterTable();
}
