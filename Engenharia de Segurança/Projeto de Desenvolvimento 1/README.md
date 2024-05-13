# Engenharia de Segurança - Projeto de Desenvolvimento I
## Mestrado em Engenharia Informática
## Projeto desenvolvido por:
* José de Matos Moreira (PG53963)
* José Mendes (PG53967)
* Pedro Freitas (PG52700)



# Introdução
Para realização do projeto em descrição neste documento, propôs-se a construção de um serviço de mensagens que permitisse aos membros de uma organização trocarem mensagens com garantias de autenticidade. Para isso, lançou-se o desafio de desenvolvimento de um servidor, responsável por manter o estado do sistema e comunicar com os diversos utilizadores, e de um serviço de cliente, executado por cada um dos utilizadores para aceder às diversas funcionalidades do *software* desenvolvido. De forma a suportar todo o projeto, foi também proposta uma tarefa extensiva de análise de requisitos e risco relacionada com a aplicação em desenvolvimento, de forma a conseguir-se seguir e justificar as melhores decisões, abordadas e implementadas, relativas à área da segurança.



# Análise de Requisitos
Como referido, uma etapa importante do presente trabalho relaciona-se com a análise de requisitos da aplicação pretendida. Deste modo, passa-se, então, a enumerar os diversos requisitos, não só, retirados do caderno de encargos original, como, também, discutidos e acordados, à parte, com a organização.


## Requisitos funcionais
Em primeiro lugar, apresentam-se os requisitos funcionais. Estes são os requisitos responsáveis por identificar funcionalidades e comportamentos do sistema. Deste modo, enumeram-se, de seguida, os requisitos funcionais sob a qual a aplicação foi desenvolvida:
* o sistema deve possuir um serviço de cliente, responsável por interagir com os utilizdores
* o sistema deve possuir um serviço de servidor, responsável por intermediar a troca de mensagens entre os diversos utilizadores e guardar o estado da aplicação
* o sistema deve ser capaz de receber mensagens de diferentes utilizadores
* o sistema deve conseguir reencaminhar as mensagens para os devidos destinatários
* o sistema deve ser capaz de identificar mensagens de erro e tratá-las devidamente
* o sistema deve ser capaz de fornecer informação sobre o seu método de operabilidade
* o sistema deve ser capaz de responder a pedidos "send" dos utilizadores, "reencaminhando" a respetiva mensagem para o destinatário pretendido
* o sistema deve ser capaz de responder a pedidos "askqueue" dos utilizadores, devolvendo informações sobre as mensagens por ler
* o sistema deve ser capaz de responder a pedidos "getmsg" dos utilizadores, devolvendo a mensagem associada ao pedido
* o sistema deve conseguir atribuir um *timestamp* a todas as mensagens enviadas por utilizadores
* o utilizador deve poder indicar a sua identidade, através da *flag* -user, sendo a mesma **userdata** aquando ausência da *flag* referida
* o utilizador deve conseguir visualizar as mensagens para si (e só para si) enviadas
* o utilizador deve ser capaz de interagir com o serviço
* o utilizador deve conseguir verificar quem lhe enviou a mensagem
* o utilizador deve conseguir terminar a interação, recorrendo ao comando **exit**

## Requisitos não funcionais
Por outro lado, surgem os requisitos não funcionais, requisitos responsáveis por oferecer informação acerca da qualidade do sistema em relação a diversos parâmetros: segurança, desempenho, usabilidade, disponibilidade, manutenção, legislação, etc. Deste modo, apresentam-se, divididos por categorias, os requisitos não funcionais:

### Segurança
* todos os intervenientes do sistema devem ser identificados por um identificador único (**UID**)
* o servidor deve registar todas as transações num ficheiro de *log*
* a comunicação entre o serviço do cliente e o serviço do servidor deve ser feita de forma a assegurar integridade, confidencialidade e autenticidade
* o servidor não deve comprometer a confidencialidade e a integridade das mensagens
* a identificação dos intervenientes do sistema deve estar contida num certificado **X.509**
* o ficheiro a conter os dados do utilizador consiste numa *keystore* **PKCS12**, contendo o certificado do utilizador e a respetiva chave privada
* todos os certificados considerados pelo sistema serão emitidos por uma **EC** dedicada

### Desempenho
* o sistema deve conseguir responder a um pedido no espaço temporal máximo de dois segundos
* o sistema deve manter a velocidade de resposta em horários de muita afluência
* o sistema deve conseguir ler da sua base de dados em, no máximo, duzentos milissegundos
* o sistema deve conseguir escrever na sua base de dados em, no máximo, quinhentos milissegundos
* o sistema deve ser capaz de escalar, automaticamente, recursos computacionais

### Disponibilidade
* o sistema deve permanecer sempre ativo, exceto em casos de manutenção
* o sistema deve ser capaz de suportar períodos de inatividade planeada

### Tecnologia
* o sistema deve ser desenvolvido na linguagem de programação **Python** ou na linguagem de programação **Java**
* o sistema deve recorrer ao formato **json**, não só, na estrutura das mensagens entre os seus intervenientes, mas, também, na persistência do seu estado
* o sistema deve ser compatível com o sistema operativo **Linux**

### Usabilidade
* o sistema deve poder ser utilizado, pelos seus utilizadores, sem nenhum treino prévio
* o sistema deve poder ser usado por indivíduos com deficiências visuais

### Legal
* o sistema deve cumprir todas as leis
* o sistema deve respeitar os direitos e as licenças de *software* de terceiros
* o sistema deve obedecer aos *standards* de proteção de dados



# Análise de Risco
A análise de risco é um processo sistemático de identificação, avaliação e mitigação dos riscos associados a uma determinada atividade, projeto, sistema ou ambiente. O objetivo principal da análise de risco é identificar potenciais ameaças ou eventos adversos que possam afetar os objetivos de um projeto ou organização, avaliar a probabilidade de ocorrência desses eventos e o impacto que podem ter e desenvolver estratégias para reduzir ou gerir esses riscos de forma eficaz. Na presente secção, faz-se, portanto, a análise de risco relativa ao sistema em questão, recorrendo ao **STRIDE**. Este último é um modelo desenvolvido para facilitar a identificação e categorização de ameaças. Deste modo, cada uma das letras do acrónimo representa uma categoria diferente: **Spoofing** (falsificação de identidade), **Tampering** (manipulação de dados), **Repudiation** (negação da autoria de uma ação), **Information Disclosure** (partilha de dados sensíveis), **Denial of Service** (sobrecarga ou interrupção dos serviços de um sistema) e **Elevation of Privilege** (ganho indevido de privilégios).

## Spoofing
Um atacante pode explorar este tipo de ataque de duas formas diferentes: fazendo-se passar por outro utilizador de forma a ter acesso às suas mensagens ou falsificando a sua identidade de forma a enviar mensagens em nome de outra pessoa.

## Tampering
Um atacante pode manipular as mensagens trocadas entre os utilizadores, quer aquando a comunicação entre um utilizador e o servidor, quer na base de dados onde as mesmas são guardadas.

## Repudiation
Um componente do sistema pode negar ter feito uma ação. Isto pode levar à perda de credibilidade entre elementos do serviço.

## Information Disclosure
Mais uma vez, quer na conexão entre um cliente e o servidor, quer na base de dados deste último, pode haver acesso ao conteúdo sensível das mensagens, resultando na divulgação de informações confidenciais.

## Denial of Service
Um utilizador mal intencionado pode sobrecarregar o servidor através do envio compulsivo de mensagens. Isto pode levar a que o serviço fique comprometido, levando à necessidade de ações de manutenção para reestabelecimento da normalidade do mesmo.

## Elevation of Privilege
Um atacante pode explorar uma vulnerabilidade associada a este tipo de ataque de modo a, por exemplo, passar a ter algum controlo sobre o componente servidor. Isto pode levar a que o mesmo tenha acesso às mensagens armazenadas.



# Características da Implementação
Nesta fase do relatório, explicam-se as várias particularidades do sitema desenvolvido. As mesmas são as que se assumem como atores principais no combate aos diversos desafios de segurança propostos e mencionados numa fase anterior do presente relatório. Adianta-se, desde já, que todos os componentes de *software* foram desenvolvidos recorrendo à linguagem de programação **python**.

## Identificação
O ficheiro que contém os dados de um interveniente é uma *keystore* **PKCS12**, composta pelo certificado do utilizador e pela sua chave privada. A utilização deste tipo de ficheiros mostra-se vantajosa na medida em que os mesmos se apresentam bastante flexíveis e compatíveis com diversas plataformas, seguros no combate ao acesso a informações sensíveis e de utilização extremamente fácil, simples e rápida. Como mencionado, um dos componentes deste ficheiro é um certificado. Como requirido pelos requisitos do sistema, o mesmo adota o padrão **X.509**, um padrão que oferece várias vantagens:
* autenticação rígida e confidencial, uma vez que podem ser utilizados por diversas entidades que pretendem provar a sua identidade, de forma segura
* criptografia forte, uma vez que a geração da chave pública, recorrendo ao mesmo, permite a utilização de criptografia assimétrica, o que proporciona um alto nível de segurança
* não repúdio, visto que o mesmo oferece várias informações sobre as entidades que o utilizam

Mostra-se importante referir que todos os certificados são produzidos por uma **EC** dedicada. Esta é confiada para efeitos de atribuição de acesso ao serviço e na consistencia das credenciais de acesso fornecidas. Com este tipo de identificação, consegue-se combater fortemente ataques de **spoofing** e **repudiation**.

## Canal de comunicação
Com o objetivo de se garantir a segurança do serviço, adotou-se a utilização de um canal seguro entre todas as comunicações realizadas entre utilizadores e o servidor. Assim, recorrendo-se ao protocolo **Transport Layer Security** e forçando-se a utilização de certificados para estabelecimento da conexão, consegue-se garantir que a comunicação entre os intervenientes é, não só, feita de forma segura mas, também, feita apenas entre utilizadores autorizados. De forma a aumentar-se, ainda mais, a segurança da comunicação, força-se o serviço a utilizar a última versão do protocolo, a versão 1.3. Deste modo, a probabilidade de acontecer um ataque relacionado a **tampering** e **information disclosure** é muito menor.

## Protocolo das mensagens
Para estruturação das diversas mensagens, recorreu-se ao formato **json**. Este último é útil na medida que oferece as seguintes vantagens:
* facilidade de leitura e escrita
* suporte a tipos de dados diversificados
* eficiência de armazenamento e de rede

## Criptografia
Para se conseguir ultrapassar os desafios colocados pelos ataques de **information disclosure** e pela possível presença de servidores maliciosos, recorreu-se a um processo de cifra das mensagens a enviar. Deste modo, quando um utilizador deseja enviar uma mensagem a um destinatário, o mesmo faz a requisição do certificado do mesmo, ao servidor, cifrando a mesma mensagem com a chave pública deste último. Isto faz com que apenas o destinatário consiga decifrar o conteúdo e ter acesso à mensagem, uma vez que é o único a possuir a chave privada.

## Assinaturas
De forma a salvaguardar-se a integridade das mensagens, implementou-se um processo de assinatura das mesmas. Deste modo e, recorrendo à sua chave privada, cada utilizador consegue assinar todas as mensagens que envia, fazendo com que o destinatário consiga verificar a integridade dessa mesma mensagem, quando para si é enviada.

## Registo
O serviço desenvolvido força a que todos os utilizadores se registem no servidor, enviando-lhe o seu certificado. Isto faz com que apenas utilizadores registados possam interagir com a aplicação e, consequentemente, enviar/receber mensagens. Este controlo adicional aumenta a segurança da aplicação, uma vez que obriga intermediários a possuírem e partilharem um certificado para conseguirem utilizar o serviço.

## Sistema de *logs*
Adicionalmente, implementou-se um sistema de *logs* que regista todas as transações feitas entre intervenientes do sistema. Isto leva a que todas as ações fiquem armazenadas, levando a que possíveis explorações de ataques do tipo **repudiation** sejam mais difíceis de acontecer. O mesmo é composto por diversos ficheiros (um por cada interveniente do sistema) com a seguinte estrutura, em cada linha:
* [UID] *timestamp* **log**

## Persistência do estado
À semelhança do protocolo das mensagens, a persistência dos dados é feita recorrendo ao formato **json**. Tendo as mesmas vantagens e, sendo realizada em apenas um ficheiro (para todos os intervenientes), essa mesma persistência é realizada com a seguinte estrutura:
* UID: identificador único do utilizador
  * cert: certificado do utilizador
  * queue: *queue* com as mensagens dirigidas ao utilizador
    * num: número único que identifica a mensagem
      * sender: remetente
      * timestamp: *timestamp* colocado, pelo servidor, aquando receção da mensagem
      * subject: assunto da mensagem
      * secret: mensagem cifrada e assinatura
      * status: *status* da mensagem (lida/não lida)



# Funcionalidades/Operabilidade do Sistema
Aqui, explica-se, resumidamente, as diversas funcionalidades implementadas e a forma de utilização das mesmas. Assim, abordam-se os diferentes componentes e explica-se o modo de operação de cada um deles.

## Servidor
Não sendo destinado à utilização dos utilizadores, o componente relativo ao servidor apenas necessita de ser inicializado. Deste modo, essa inicialização é feita através do comando **python3 server.py**, recorrendo à linha de comandos.

## Cliente
Por outro lado, o serviço do cliente destina-se à utilização dos membros da organização para qual foi desenvolvida a aplicação. A inicialização do mesmo pode ser feita de três formas distintas:
* **python3 cliente.py help**: imprime informações acerca da utilização do serviço do cliente
* **python3 cliente.py**: inicializa o serviço do cliente, atribuindo a entidade **userdata** ao mesmo
* **python3 cliente.py -user \<UID\>**: inicializa o serviço do cliente relativo ao utilizador com a entidade **UID**

Uma vez que a aplicação se encontra inicializada, passa-se a explicar os vários comandos que podem ser introduzidos pelo utilizador:
* **signup**: comando que permite o registo do utilizador, enviando o certificado do mesmo ao servidor, fazendo com que este último crie um registo do utilizador na sua memória
* **exit**: comando que permite, ao utilizador, terminar a conexão com o servidor, de forma correta
* **askqueue**: comando que pede, ao servidor, o envio de metadados sobre as mensagens que ainda se encontram por ler, com o seguinte formato, por mensagem:
  * \<NUM\>:\<SENDER\>:\<TIME\>:\<SUBJECT\>
* **getmsg \<NUM\>**: comando que solicita, ao servidor, o envio da mensagem com o respetivo número. Quando a mensagem existe, a mesma é enviada e atualizada como "lida". Quando não existe, é enviada uma mensagem de erro. Por outro lado, se o processo de decifragem/verificação de assinatura der erro, também é impressa uma mensagem de erro
* **send \<UID\> \<SUBJECT\>**: comando que permite o envio de uma mensagem para um destinatário, com um pequeno assunto. Quando o destinatário não se encontra registado, é enviada uma mensagem de erro

Mostra-se importante referir que o utilizador **userdata**, ou seja, o utilizador *default* do programa, é apenas utilizado para efeitos de testes de segurança, uma vez que possui um certificado errado.

# Aspetos a melhorar
Apesar de todo o trabalho desenvolvido, há aspetos que, na opinião da equipa de trabalho, podiam estar feitos de forma a oferecerem mais segurança à aplicação. Passa-se, assim, a explicar os mesmos:
* componente de certificação, isto é, elaborar um componente de *software* responsável por gerir, de forma fiável e segura, a produção de certificados
* não confiar no servidor para atribuições de *timestamp* às mensagens, utilizando, alternadamente, um acordo de *timestamp* entre os utilizadores ou verificação através dos certificados
* implementar controlo de fluxo de mensagens, não permitindo que um utilizador sobrecarregue o serviço
* implementar um certo tipo de reforço da segurança dos arquivos de *log*, impedindo que os mesmos sejam alvo de ataques maliciosos
* aplicação de criptografia ao ficheiro de persistência de dados do sistema, reforçando o impedimento de acessos indevidos

# Conclusão
Em conclusão, o desenvolvimento de um sistema de mensagens, com ênfase na segurança, requer uma abordagem abrangente e multifacetada. Ao longo deste projeto, identificaram-se e implementaram-se diversos mecanismos de segurança para garantir a autenticidade, integridade, confidencialidade e disponibilidade das comunicações entre os utilizadores e o servidor.

A análise de requisitos e riscos permitiu identificar as necessidades específicas do sistema e os potenciais pontos vulneráveis que poderiam ser explorados por agentes maliciosos. Com base nessa análise, foram implementadas medidas de segurança, como autenticação de usuários por meio de certificados **X.509**, comunicação segura por meio do protocolo **TLS** e criptografia de mensagens e assinaturas digitais para garantir a autenticidade e integridade das comunicações.

Além disso, a implementação de políticas de controlo de acesso, gestão de exceções, validação de dados de entrada e a adoção de boas práticas de desenvolvimento seguro contribuíram para fortalecer a segurança do sistema e mitigar possíveis vulnerabilidades.

No entanto, é importante reiterar que a segurança é um processo contínuo e em constante evolução. Portanto, é fundamental realizar testes de segurança regulares, manter as equipas atualizadas sobre as últimas ameaças e vulnerabilidades e preparar os diferentes intervenientes para que consigam responder, de forma eficaz, a qualquer incidente de segurança que possa surgir.

Por fim, o sucesso na construção de um sistema de mensagens seguro depende da colaboração e do compromisso de todos os envolvidos, desde os desenvolvedores e administradores até aos próprios utilizadores, para garantir que as melhores práticas de segurança sejam seguidas e que o sistema permaneça protegido contra ameaças em constante evolução.