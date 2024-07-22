**Problema**

O objetivo do trabalho proposto é a automatização da criação de ficheiros "pyproject.toml".

**Solução**

Para resolução do problema e, recorrendo às bibliotecas: **jinja2**, **glob**, **pathlib** e **json**, procedeu-se às seguintes etapas:
* leitura do nome do módulo sob o qual se quer elaborar o **pyproject**, através do **glob** ou, em caso de resultado nulo, através do *input*
* tentativa de leitura do ficheiro **metadata.json**, situado na diretoria principal, recorrendo ao **path**
* em caso de sucesso, leitura das variáveis **author** e **email**, caso contrário, pedido de *input* das mesmas
* pedido de *input* da versão do **python** requerida
* leitura, mais uma vez, recorrendo ao *input*, das dependências necessárias
* interpolação das variáveis, recorrendo ao **jinja2** e, após *render*, escrita do resultado no ficheiro **pyproject.toml**