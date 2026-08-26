const services = [
  ['01', 'Direito empresarial', 'Estruturação societária, contratos e suporte estratégico para decisões seguras.'],
  ['02', 'Contencioso cível', 'Atuação firme e criteriosa em disputas complexas e negociações sensíveis.'],
  ['03', 'Patrimônio e sucessão', 'Planejamento jurídico para proteger conquistas e construir legados duradouros.'],
];

export default function Home() {
  return (
    <main>
      <header className="nav"><a className="brand" href="#inicio" aria-label="Aurum Advocacia, início"><span className="brand-mark">A</span><span>AURUM<small>ADVOCACIA</small></span></a><nav aria-label="Navegação principal"><a href="#sobre">O escritório</a><a href="#atuacao">Atuação</a><a href="#contato">Contato</a></nav><a className="nav-cta" href="#contato">Agendar conversa</a></header>
      <section className="hero" id="inicio"><div className="hero-shade" /><div className="hero-content"><p className="eyebrow">ESTRATÉGIA JURÍDICA • SÃO PAULO</p><h1>Clareza para decidir.<br /><em>Experiência</em> para proteger.</h1><p className="hero-copy">Soluções jurídicas precisas para empresas, famílias e patrimônios que exigem visão de longo prazo.</p><a className="button light" href="#atuacao">Conheça nossa atuação <span>→</span></a></div><div className="scroll-note">ROLE PARA DESCOBRIR <span>↓</span></div></section>
      <section className="intro" id="sobre"><p className="section-label">01 — O ESCRITÓRIO</p><div><h2>Direito não é apenas resposta.<br />É <em>direção.</em></h2><p>Unimos profundidade técnica, escuta atenta e entendimento de negócios. Cada caso recebe uma estratégia clara, construída para reduzir incertezas e criar caminhos consistentes.</p><a className="text-link" href="#contato">Nossa forma de trabalhar ↗</a></div></section>
      <section className="services" id="atuacao"><div className="services-head"><p className="section-label">02 — ÁREAS DE ATUAÇÃO</p><h2>Conhecimento que se transforma em <em>resultado.</em></h2></div><div className="service-list">{services.map(([number,title,copy])=><article key={number}><span>{number}</span><h3>{title}</h3><p>{copy}</p><a href="#contato" aria-label={`Saiba mais sobre ${title}`}>↗</a></article>)}</div></section>
      <section className="statement"><p>Rigor nos detalhes.</p><h2>Visão no todo.</h2></section>
      <section className="numbers" aria-label="Números do escritório"><div><strong>18</strong><span>anos de experiência</span></div><div><strong>320+</strong><span>casos assessorados</span></div><div><strong>12</strong><span>especialistas</span></div><div><strong>06</strong><span>estados atendidos</span></div></section>
      <section className="contact" id="contato"><div><p className="section-label">03 — CONTATO</p><h2>Vamos conversar sobre o que <em>importa.</em></h2></div><form><label>Nome<input type="text" placeholder="Seu nome" /></label><label>E-mail<input type="email" placeholder="voce@empresa.com" /></label><label>Como podemos ajudar?<textarea rows={3} placeholder="Conte-nos brevemente sobre sua necessidade" /></label><button type="submit">Enviar mensagem <span>→</span></button></form></section>
      <footer><div className="brand"><span className="brand-mark">A</span><span>AURUM<small>ADVOCACIA</small></span></div><p>Alameda Santos, 000 — São Paulo, SP<br />contato@aurum.adv.br</p><p>© 2026 Aurum Advocacia</p></footer>
    </main>
  );
}
