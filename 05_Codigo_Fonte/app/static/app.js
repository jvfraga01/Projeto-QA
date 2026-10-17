// Tema claro/escuro (preferência salva no navegador)
const tema = localStorage.getItem("tema") || "light";
document.documentElement.setAttribute("data-theme", tema);
document.addEventListener("DOMContentLoaded", () => {
  const raiz = document.documentElement, botao = document.getElementById("btn-tema");
  if (botao) {
    botao.textContent = raiz.dataset.theme === "dark" ? "☀️" : "🌙";
    botao.addEventListener("click", () => {
      const novo = raiz.dataset.theme === "dark" ? "light" : "dark";
      raiz.dataset.theme = novo; localStorage.setItem("tema", novo);
      botao.textContent = novo === "dark" ? "☀️" : "🌙";
    });
  }
  document.querySelectorAll("[data-print]").forEach(b => b.addEventListener("click", () => window.print()));
  document.querySelectorAll("form[data-confirm]").forEach(f =>
    f.addEventListener("submit", e => { if (!confirm(f.dataset.confirm)) e.preventDefault(); }));
  document.querySelectorAll("[data-auto-submit]").forEach(s =>
    s.addEventListener("change", () => s.form.submit()));
  // Mostra só os campos do tipo de colaborador escolhido
  const tipo = document.getElementById("tipo");
  if (tipo) {
    const atualiza = () => document.querySelectorAll(".extra").forEach(
      d => { d.hidden = d.dataset.tipo !== tipo.value; });
    tipo.addEventListener("change", atualiza); atualiza();
  }
});
