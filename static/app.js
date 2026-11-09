(() => {
  'use strict';

  const $ = (selector) => document.querySelector(selector);
  const editor = $('#editor');
  const output = $('#output');

  const state = {
    curriculum: null,
    lesson: null,
    exercise: null,
    busy: false,
  };

  let lessonToken = 0;

  // ---------------------------------------------------------------- 工具
  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }

  let toastTimer = null;
  function toast(message) {
    const element = $('#toast');
    element.textContent = message;
    element.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => element.classList.remove('show'), 2600);
  }

  async function api(path, options = {}) {
    const response = await fetch(path, options);
    let data = {};
    try {
      data = await response.json();
    } catch (_) {
      /* 非 JSON 响应 */
    }
    if (!response.ok) {
      throw new Error(data.error || `请求失败（HTTP ${response.status}）`);
    }
    return data;
  }

  function postJSON(path, payload) {
    return api(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  // ---------------------------------------------------------------- 侧栏
  function updateOverall() {
    const total = state.curriculum ? state.curriculum.total : 0;
    const done = state.curriculum ? state.curriculum.done : 0;
    $('#overallText').textContent = `${done} / ${total}`;
    $('#overallBar').style.width = total ? `${(done / total) * 100}%` : '0%';
  }

  function renderCurriculum() {
    const nav = $('#curriculum');
    const scrollTop = nav.scrollTop;
    nav.innerHTML = '';
    for (const stage of state.curriculum.stages) {
      const section = document.createElement('section');
      section.className = 'stage';

      const head = document.createElement('div');
      head.className = 'stage-head';
      const name = document.createElement('span');
      name.textContent = stage.title;
      head.appendChild(name);
      if (stage.locked) {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = '待开放';
        head.appendChild(tag);
      }
      section.appendChild(head);

      if (stage.locked) {
        const summary = document.createElement('p');
        summary.className = 'stage-summary';
        summary.textContent = stage.summary;
        section.appendChild(summary);
      } else {
        for (const lesson of stage.lessons) {
          const button = document.createElement('button');
          button.className = 'lesson';
          if (lesson.status === 'done') button.classList.add('done');
          if (state.lesson && state.lesson.id === lesson.id) button.classList.add('active');

          const dot = document.createElement('span');
          dot.className = 'dot';
          const text = document.createElement('span');
          text.className = 'lesson-title';
          text.textContent = lesson.title;
          const minutes = document.createElement('span');
          minutes.className = 'lesson-min';
          minutes.textContent = `${lesson.minutes}′`;

          button.append(dot, text, minutes);
          button.addEventListener('click', () => selectLesson(lesson.id));
          section.appendChild(button);
        }
      }
      nav.appendChild(section);
    }
    nav.scrollTop = scrollTop;
    updateOverall();
  }

  async function refreshCurriculum() {
    state.curriculum = await api('/api/curriculum');
    renderCurriculum();
  }

  // ---------------------------------------------------------------- 课程
  function draftKey(id) {
    return `pylab:draft:${id}`;
  }

  let saveTimer = null;
  function saveDraft() {
    if (!state.lesson || !state.exercise) return;
    localStorage.setItem(draftKey(state.lesson.id), editor.value);
  }
  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveDraft, 400);
  }

  async function selectLesson(id) {
    saveDraft();
    closeSolution();
    const token = ++lessonToken;
    try {
      const lesson = await api(`/api/lesson?id=${encodeURIComponent(id)}`);
      if (token !== lessonToken) return;
      state.lesson = lesson;
      state.exercise = lesson.exercise;

      $('#stageLabel').textContent = lesson.stage;
      $('#lessonTitle').textContent = lesson.title;
      $('#lessonMeta').textContent = lesson.type === 'coding'
        ? `${lesson.minutes} 分钟 · 通过检查自动完成`
        : `${lesson.minutes} 分钟`;
      $('#content').innerHTML = lesson.html;
      $('#content').scrollTop = 0;
      renderMarkButton();

      if (lesson.exercise) {
        $('#workspace').hidden = false;
        $('#split').classList.remove('no-ws');
        $('#exerciseId').textContent = `#${lesson.exercise.id}`;
        const saved = localStorage.getItem(draftKey(id));
        editor.value = saved !== null ? saved : lesson.exercise.starter;
        editor.scrollTop = 0;
        updateGutter();
        clearOutput('运行或检查的结果会显示在这里');
      } else {
        $('#workspace').hidden = true;
        $('#split').classList.add('no-ws');
      }

      renderCurriculum();
    } catch (error) {
      toast(error.message);
    }
  }

  function renderMarkButton() {
    const button = $('#markBtn');
    if (!state.lesson) {
      button.hidden = true;
      return;
    }
    // 编程题由判题结果决定是否完成，不允许手动标记，避免制造虚假进度
    if (state.lesson.type === 'coding') {
      button.hidden = true;
      return;
    }
    const done = state.lesson.status === 'done';
    button.hidden = false;
    button.textContent = done ? '已完成' : '标记完成';
    button.classList.toggle('done', done);
  }

  async function toggleDone() {
    if (!state.lesson) return;
    const next = state.lesson.status === 'done' ? 'todo' : 'done';
    try {
      await postJSON('/api/progress', { lesson_id: state.lesson.id, status: next });
      state.lesson.status = next;
      renderMarkButton();
      await refreshCurriculum();
      toast(next === 'done' ? '已标记完成' : '已取消完成标记');
    } catch (error) {
      toast(error.message);
    }
  }

  // ---------------------------------------------------------------- 编辑器
  function updateGutter() {
    const count = editor.value.split('\n').length;
    const lines = [];
    for (let i = 1; i <= count; i += 1) lines.push(i);
    $('#gutter').textContent = lines.join('\n');
  }

  function clearOutput(message) {
    output.innerHTML = `<div class="output-empty">${escapeHtml(message)}</div>`;
  }

  function setBusy(busy) {
    state.busy = busy;
    for (const id of ['#runBtn', '#checkBtn', '#resetBtn']) {
      $(id).disabled = busy;
    }
  }

  // ---------------------------------------------------------------- 运行
  function renderRunResult(result) {
    const parts = [];
    const exitLabel = result.exit_code === null ? '已超时' : `退出码 ${result.exit_code}`;
    const exitClass = result.exit_code === 0 ? 'ok' : 'bad';
    parts.push(
      `<div class="out-meta">` +
        `<span class="chip ${exitClass}">${escapeHtml(exitLabel)}</span>` +
        `<span class="chip">${result.duration_ms} ms</span>` +
      `</div>`
    );
    if (result.stdout) {
      parts.push(`<pre class="out-pre">${escapeHtml(result.stdout)}</pre>`);
    }
    if (result.stderr) {
      parts.push(`<pre class="out-pre err">${escapeHtml(result.stderr)}</pre>`);
    }
    if (!result.stdout && !result.stderr) {
      parts.push('<div class="hint">程序正常结束，没有任何输出。用 print() 打印点东西看看。</div>');
    }
    output.innerHTML = parts.join('');
  }

  async function runCode() {
    if (!state.lesson || !state.exercise || state.busy) return;
    setBusy(true);
    output.innerHTML = '<div class="hint">运行中…</div>';
    try {
      const result = await postJSON('/api/run', {
        lesson_id: state.lesson.id,
        code: editor.value,
      });
      renderRunResult(result);
    } catch (error) {
      output.innerHTML = `<pre class="out-pre err">${escapeHtml(error.message)}</pre>`;
    } finally {
      setBusy(false);
    }
  }

  // ---------------------------------------------------------------- 检查
  function renderCheckResult(result) {
    const parts = [];
    const total = result.results.length;
    const passed = result.results.filter((item) => item.ok).length;

    if (result.ok) {
      parts.push(`<div class="summary-title ok">全部通过 · ${passed} / ${total}</div>`);
    } else if (result.error) {
      parts.push('<div class="summary-title bad">未能判定</div>');
    } else {
      parts.push(`<div class="summary-title bad">未通过 · ${passed} / ${total}</div>`);
    }

    if (result.error) {
      parts.push(`<pre class="out-pre err">${escapeHtml(result.error)}</pre>`);
    }

    if (total) {
      parts.push('<div class="check-list">');
      for (const item of result.results) {
        parts.push(
          `<div class="check-item ${item.ok ? 'pass' : 'fail'}">` +
            `<span class="check-icon">${item.ok ? '✓' : '✕'}</span>` +
            `<span class="check-body">` +
              `<div class="check-name">${escapeHtml(item.name)}</div>` +
              (item.msg ? `<div class="check-msg">${escapeHtml(item.msg)}</div>` : '') +
            `</span>` +
          `</div>`
        );
      }
      parts.push('</div>');
    }

    if (result.stderr && !result.ok) {
      parts.push(`<pre class="out-pre err">${escapeHtml(result.stderr)}</pre>`);
    }

    output.innerHTML = parts.join('');
  }

  async function checkCode() {
    if (!state.lesson || !state.exercise || state.busy) return;
    setBusy(true);
    output.innerHTML = '<div class="hint">正在运行测试…</div>';
    try {
      const result = await postJSON('/api/check', {
        lesson_id: state.lesson.id,
        code: editor.value,
      });
      renderCheckResult(result);
      if (result.ok) {
        state.lesson.status = 'done';
        renderMarkButton();
        await refreshCurriculum();
      }
    } catch (error) {
      output.innerHTML = `<pre class="out-pre err">${escapeHtml(error.message)}</pre>`;
    } finally {
      setBusy(false);
    }
  }

  function resetCode() {
    if (!state.exercise || !state.lesson) return;
    editor.value = state.exercise.starter;
    localStorage.removeItem(draftKey(state.lesson.id));
    updateGutter();
    clearOutput('已恢复起始代码');
  }

  // ---------------------------------------------------------------- 参考答案
  async function showSolution() {
    if (!state.lesson || !state.exercise) return;
    try {
      const data = await api(`/api/solution?id=${encodeURIComponent(state.lesson.id)}`);
      $('#solutionCode').textContent = data.code;
      $('#solutionModal').hidden = false;
    } catch (error) {
      toast(error.message);
    }
  }

  function closeSolution() {
    $('#solutionModal').hidden = true;
  }

  async function copySolution() {
    try {
      await navigator.clipboard.writeText($('#solutionCode').textContent);
      toast('已复制到剪贴板');
    } catch (_) {
      toast('复制失败，请手动选中');
    }
  }

  // ---------------------------------------------------------------- 事件
  editor.addEventListener('input', () => {
    updateGutter();
    scheduleSave();
  });

  editor.addEventListener('scroll', () => {
    $('#gutter').scrollTop = editor.scrollTop;
  });

  editor.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') {
      event.preventDefault();
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      editor.setRangeText('    ', start, end, 'end');
      updateGutter();
      scheduleSave();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      if (event.shiftKey) {
        checkCode();
      } else {
        runCode();
      }
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !$('#solutionModal').hidden) {
      closeSolution();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      if (event.shiftKey) {
        checkCode();
      } else {
        runCode();
      }
    }
  });

  $('#runBtn').addEventListener('click', runCode);
  $('#checkBtn').addEventListener('click', checkCode);
  $('#resetBtn').addEventListener('click', resetCode);
  $('#solutionBtn').addEventListener('click', showSolution);
  $('#closeSolution').addEventListener('click', closeSolution);
  $('#copySolution').addEventListener('click', copySolution);
  $('#solutionModal').addEventListener('click', (event) => {
    if (event.target.id === 'solutionModal') closeSolution();
  });
  $('#markBtn').addEventListener('click', toggleDone);
  window.addEventListener('beforeunload', saveDraft);

  // ---------------------------------------------------------------- 启动
  async function init() {
    try {
      state.curriculum = await api('/api/curriculum');
      renderCurriculum();
      const opening = state.curriculum.stages
        .filter((stage) => !stage.locked)
        .flatMap((stage) => stage.lessons)[0];
      if (opening) {
        await selectLesson(opening.id);
      }
    } catch (error) {
      toast(error.message);
      $('#curriculum').innerHTML = '<div class="loading">加载失败，请确认服务已启动</div>';
    }
  }

  init();
})();
