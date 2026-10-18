# Projeto_FolhaPagamento

Sistema de Folha de Pagamento desenvolvido para o Trabalho Integrador (A1 e A3) da unidade curricular
**Garantia da Qualidade de Software**.

**Equipe:** João Vitor Fraga, Pedro Kolling, Yuri Soares e Luiggi Bortolini · **Versão:** 0.1 (A1) · **Linguagem:** Python 3 + Flask + SQLite

## Como usar (resumo)
1. Instale o Python 3.10+ (ou deixe o `iniciar.bat` oferecer a instalação).
2. Dê dois cliques em `05_Codigo_Fonte/iniciar.bat` (Windows) ou execute `05_Codigo_Fonte/iniciar.sh`.
3. Entre com matrícula **1** e senha **01012000** e troque a senha no menu.

Comandos de terminal, requisitos e solução de problemas: [`05_Codigo_Fonte/INSTALACAO.md`](05_Codigo_Fonte/INSTALACAO.md).

## Estrutura de entrega
| Pasta | Conteúdo | Entrega |
|---|---|---|
| `01_Requisitos` | Documento de Visão, ERS (com rastreabilidade) | A1 |
| `02_Analise` | Casos de Uso, diagramas UML | A1 |
| `03_Projeto` | Arquitetura, planejamento (EAP, cronograma, responsabilidades) | A1 |
| `04_Testes` | Plano de Testes, Casos de Teste (37) | A1 |
| `05_Codigo_Fonte` | Sistema, testes automatizados, instruções | A1 (estrutura) / A3 |
| `06_Banco_Dados` | Script do banco | A3 |
| `07_Executavel` | Pacote executável | A3 |
| `08_Manuais` | Manual do usuário e técnico | A3 |
| `09_Homologacao` | Testes de aceitação e termo | A3 |
| `10_Qualidade` | PGQ (A1); defeitos, métricas e relatório final (A3) | A1 / A3 |
| `11_Apresentacao` | Slides e roteiro | A3 |

Os diagramas estão em **Mermaid** (aparecem prontos no GitHub e no VS Code com a extensão Markdown Preview Mermaid).

## Testes
```bash
cd 05_Codigo_Fonte
python -m unittest discover -v      # 29 testes
```

