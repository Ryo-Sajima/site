const load_btn = document.getElementById('load-button');
const btn_txt = document.getElementById('button-text');

function ready() {
    load_btn.disabled = false;
}

function btn_click() {
    load_btn.classList.add('button-loading');
    load_btn.disabled = true;
}

function btn_success() {
    load_btn.classList.remove('button-loading');
    btn_txt.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" id="checkmark" class="bi bi-check-lg" viewBox="0 0 16 16"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/></svg>';
    load_btn.classList.add('btn-success');
    load_btn.classList.remove('btn-primary');
    load_btn.disabled = true;
}

function btn_failure() {
    load_btn.classList.remove('button-loading');
    btn_txt.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="bi bi-x-lg" viewBox="0 0 16 16"><path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/></svg>';
    load_btn.classList.add('btn-danger');
    load_btn.classList.remove('btn-primary');
    load_btn.disabled = true;
}
