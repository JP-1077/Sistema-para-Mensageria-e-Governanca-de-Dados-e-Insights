# 🌐 Sistema de Mensageria para Governça e Comunicação de Dados


🎯 1. Objetivo do Sistema
---

Desenvolver uma aplicação que realiza:

* Coleta de Dados analiticos através de uma banco de dados da nuvem GCP (Google Cloud Platform).
* Realização de toda uma camada de processamento, transformação e filtragem nos dados coletados
* Aplicaçaõ de Regras de negócios nesses dados
* Consumo de APIs do Microsoft Teams
* Envio de Relatorios informacionais para monitoramento das informações

---

✍🏾 2. System Design
---

### Arquitetura do Sistema

O projeto seguiu um padrão de arquitetura MVC (ModelO - Visão - Controlador) Model para dados e lógica de negócios, Visão para a interface do usuário e Controlador para processar a entrada do usuário e conectar o modelo e a visão. Desta forma, iremos conseguir trazer determinados ganhos para aplicação. São eles:

* Separação de Responsabilidades
* Facilidade na manutenção
* Reutilização de código
* Desenvolvimento Paralelo

