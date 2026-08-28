import logoChindler from '../../logo_chindler_peq_nova.png';
import MobileMenu from '../MobileMenu';
import { sitePath } from '../site-paths';

export const dynamic = 'force-static';

export default function PrivacyPage() {
  return <main className="privacy-page">
    <header className="nav privacy-nav"><a className="brand" href={sitePath('/')} aria-label="Chindler, início"><img className="brand-logo" src={logoChindler.src} alt="Chindler" /></a><nav aria-label="Navegação principal"><a href={sitePath('/imoveis/')}>Balcão de Imóveis</a><div className="nav-dropdown"><button type="button" aria-haspopup="true">Condomínio <span aria-hidden="true">⌄</span></button><div className="dropdown-menu"><a href={sitePath('/condominio/servicos/')}>Serviços</a><a href={sitePath('/condominio/diferenciais/')}>Diferenciais da Chindler</a><a href={sitePath('/condominio/taxa-administrativa/')}>Taxa Administrativa</a></div></div><a href={sitePath('/#contato')}>Contato</a></nav><a className="nav-cta" href="https://admin107486.superlogica.net/clients/areadocondomino" target="_blank" rel="noreferrer">Portal do Cliente</a><MobileMenu /></header>
    <section className="privacy-hero"><div><p className="eyebrow">PRIVACIDADE E PROTEÇÃO DE DADOS</p><h1>Política de <em>Privacidade.</em></h1><p>Versão 1.0 • Atualizada em agosto de 2026</p></div></section>
    <article className="privacy-content">
      <section><h2>1. Quem trata seus dados</h2><p>A Chindler atua como controladora dos dados enviados em seus canais digitais. Solicitações relacionadas à privacidade podem ser encaminhadas para <a href="mailto:contato@chindler.com.br">contato@chindler.com.br</a>.</p></section>
      <section><h2>2. Dados coletados</h2><p>No formulário de interesse coletamos nome, telefone, e-mail, mensagem, imóvel relacionado, data do consentimento e informações técnicas necessárias à segurança e ao controle de envios.</p></section>
      <section><h2>3. Finalidade</h2><p>Os dados são utilizados para responder à solicitação, esclarecer dúvidas, organizar o atendimento e, quando solicitado, agendar visitas ou dar continuidade à negociação imobiliária.</p></section>
      <section><h2>4. Compartilhamento e segurança</h2><p>O acesso é limitado à equipe autorizada e aos fornecedores técnicos necessários ao funcionamento seguro da plataforma. A Chindler não comercializa os dados informados no formulário.</p></section>
      <section><h2>5. Retenção</h2><p>Os dados dos interessados são mantidos por até dois anos após o último atendimento. Ao final desse período, os dados pessoais são anonimizados, salvo quando a conservação for necessária para atender uma obrigação legal ou outra hipótese permitida.</p></section>
      <section><h2>6. Seus direitos</h2><p>O titular pode solicitar confirmação e acesso, correção, informações sobre o tratamento, revogação do consentimento e, quando aplicável, anonimização, bloqueio ou eliminação. A solicitação poderá exigir confirmação de identidade para proteger o próprio titular.</p></section>
      <section><h2>7. Atualizações</h2><p>Esta política pode ser atualizada para refletir mudanças legais ou operacionais. A versão aceita no formulário e a data do consentimento permanecem registradas no sistema.</p></section>
      <p className="privacy-reference">Consulte também a <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm" target="_blank" rel="noreferrer">Lei Geral de Proteção de Dados Pessoais</a>.</p>
    </article>
    <footer><div className="brand"><img className="brand-logo footer-logo" src={logoChindler.src} alt="Chindler" /></div><div className="footer-details"><p>Av. Rio Branco, 109 - 18º Andar<br />Centro - Rio de Janeiro - RJ</p><a className="footer-contact" href="tel:+552122216453"><span aria-hidden="true">☎</span> (21) 2221-6453</a><br /><a className="footer-privacy" href={sitePath('/privacidade/')}>Política de Privacidade</a></div><p>© 2026 Chindler</p></footer>
  </main>;
}
