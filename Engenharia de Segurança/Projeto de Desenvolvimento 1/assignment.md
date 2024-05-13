# Projecto de Desenvolvimento I (PD1)

Pretende-se construir um serviço de mensagens que permita aos membros de uma organização trocarem mensagens com garantias de autenticidade. O serviço será suportado por um servidor responsável por manter o estado da aplicação e interagir com os utilizadores do sistema. Todo os intervenientes do sistema (servidor e utilizadores) serão identificados por *identificador único* `<UID>` (mais detalhes sobre este identificador abaixo).

Note que o projecto consiste essencialmente na análise de requisitos e risco associada a uma hipotética aplicação, sendo que na respectiva implementação irá consistir basicamente na combinação de diferentes componentes criptográficas desenvolvidas nas aulas práticas. Mais uma vez, a linguagem de programação é deixada em aberto -- reconhece-se que a adopção do *Python* acaba por ser facilitada por os guiões estarem orientados a essa linguagem, mas **incentiva-se** (e até se **desafia**) os grupos a adoptarem outras linguagem de desenvolvimento.


## Descrição

O projecto consistirá no desenvolvimento de um sistema Cliente/Servidor, em que a aplicação `cliente` será executada por cada utilizador para aceder à funcionalidade oferecida pelo serviço, e o `servidor` será responsável por responder às solicitações dos utilizadores e manter o estado do sistema.

A descrição que se apresenta agora deve ser entendida como o *caderno de encargos original* contendo a funcionalidade solicitada pela entidade que "encomendou" o serviço. É natural que no desenvolvimento do sistema haja necessidade de refinar (e até ajustar) a funcionalidade, sendo que se nesse caso deve o próprio grupo **simular** uma hipotética interacção entre a equipa de desenvolvimento e quem solicitou o serviço, arbitrando "respostas plausíveis e interessantes" para as eventuais questões que surjam.

### Comandos da aplicação cliente

Os utilizadores do sistema irão interagir com recurso à aplicação `cliente` que aceitará os seguintes comandos (com correspondentes opções de linha de comando):

- `-user <FNAME>` -- argumento opcional (que deverá surgir sempre em primeiro lugar) que especifica o ficheiro com dados do utilizador. Por omissão, será assumido que esse ficheiro é `userdata.p12`.
- `send <UID> <SUBJECT>` -- envia uma mensagem com assunto `<SUBJECT>` destinada ao utilizador com identificador `<UID>`. O conteúdo da mensagem será lido do `stdin`, e o tamanho deve ser limitado a 1000 bytes.
- `askqueue` -- solicita ao servidor que lhe envie a lista de mensagens **não lidas** da *queue* do utilizador. Para cada mensagem na *queue*, é devolvida uma linha contendo: `<NUM>:<SENDER>:<TIME>:<SUBJECT>`, onde `<NUM>` é o número de ordem da mensagem na *queue* e `<TIME>` um *timestamp* adicionado pelo servidor que regista a altura em que a mensagem foi recebida. <!--Nas mensagens do tipo ficheiro, considera-se que o `<SUBJECT>` é `FILE <FNAME>`-->
- `getmsg <NUM>` -- solicita ao servidor o envio da mensagem da sua *queue* com número `<NUM>`. No caso de sucesso, a mensagem será impressa no `stdout`. Uma vez enviada, essa mensagem será marcada como lida, pelo que não será listada no próximo comando `askqueue` (mas pode voltar a ser pedida pelo cliente).
- `help` -- imprime instruções de uso do programa.

No caso de erro na interpretação do comando (e.g. número incorrecto de argumentos), a aplicação deverá emitir em `stderr` o erro `MSG SERVICE: command error!`, seguido das instruções de uso apresentadas pelo comando `help`.

### Características de segurança pretendidas

 1. Toda a comunicação entre a aplicação `cliente` e `servidor` deve ser protegidas contra acesso ilegítimo e/ou manipulação (incluindo de outros utilizadores do sistema).
 1. Confia-se no servidor para efeitos da atribuição da "hora/data" associada às mensagems, e que este não compromete a confidencialidade das mensagens tratadas. No entanto não lhe deve ser permitida a manipulação do conteúdo ou destino dessas mensagens.
 1. Os clientes, ao receberem uma mensagem, devem poder verificar que a mensagem foi efectivamente enviada pelo `<SENDER>` especificado e a si dirigida. No caso de erro, deve ser enviado para para `stderr` a mensagem respectiva, nomeadamente:
     - `MSG SERVICE: unknown message!` -- no caso da mensagem não existir na *queue* do utilizador;
     - `MSG SERVICE: verification error!` -- no caso da verificação falhar.

### Identificação e credenciais dos utilizadores

A organização já dispõe de uma infraestrutura de certificação, pelo que sugere que as credenciais do sistema passem pela utilização desses certificados. Assim, sugere que:

 1. A identificação dos intervenientes do sistema seja representada na informação contida num certificado X509. Considera-se que o nome do campo `subject` desse certificado contém pelo menos os atributos: [`PSEUDONYM`](https://cryptography.io/en/stable/x509/reference/#cryptography.x509.oid.NameOID.PSEUDONYM), que irá armazenar o `<UID>` do utilizador a adoptar pelo sistema; [`CN`](https://cryptography.io/en/stable/x509/reference/#cryptography.x509.oid.NameOID.COMMON_NAME), que contém um nome mais informativo (e.g. nome completo), e o atributo [`OU`](https://cryptography.io/en/stable/x509/reference/#cryptography.x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME) que irá conter a string `MSG SERVICE`. O identificador do servidor será `SERVER`.
 1. O ficheiro contendo os dados do cliente (por omissão, `userdata.p12`) irá consistir numa keystore `PKCS12` contendo o certificado do utilizador e a respectiva chave privada.
 1. Todos os certificados considerados pelo sistema serão emitidos por uma EC dedicada (com `<UID>` `CA`). Essa entidade é confiada para efeitos de atribuição do acesso ao serviço e na consistencia das credenciais de acesso fornecidas (e.g. unicidade dos `<UID>` dos utilizados). São inclusivamente disponibilizados certificados de teste que podem ser usados durante o desenvolvimento da aplicação:
     - [`CA.crt`](pd1/CA.crt) -- certificado auto-assinado da EC do sistema;
     - [`SERVER.p12`](pd1/SERVER.p12),[`CLI1.p12`](pd1/CLI1.p12), [`CLI2.p12`](pd1/CLI2.p12) e [`CLI3.p12`](pd1/CLI3.p12) -- *keystores* contendo os certificados e chave privadas do servidor e três utilizadores. As *keystores* não dispõe de qualquer protecção[^1]. Por conveniencia, as *keystores* contém ainda o certificado da EC do sistema.

[^1]: Prática seguida para facilitar o processo de desenvolvimento (mas claramente desaconselhada se se estivesse a falar de um produto final...).

Note que pode facilmente extrair o conteúdo das *keystores* recorrendo à classe [PKCS12](https://cryptography.io/en/stable/hazmat/primitives/asymmetric/serialization/#pkcs12) da biblioteca `cryptography`. Por exemplo:

```python
def get_userdata(p12_fname):
    with open(p12_fname, "rb") as f:
        p12 = f.read()
    password = p12_passwd
    #password = getpass("Password? ").encode()
    (private_key, user_cert, [ca_cert]) = pkcs12.load_key_and_certificates(p12, password)
    return (private_key, user_cert, ca_cert)
```

## Possíveis melhoramentos

Como se referiu, o projecto atrás apresentado oferece suficiente liberdade para permitir incluir melhorias tanto em termos de funcionalidade e/ou garantias de segurança; aspectos de implementação; etc. Os grupos são incentivados a identificar e implementar essas melhorias. Podem ainda ser propostas e analisadas melhorias no relatório que acabem por não ser implementadas (e.g. por falta de tempo e/ou porque envolveriam alterações substanciais na arquitectura).

Algumas possibilidades:
- Suportar a componente de certificação (i.e. gerir a produção dos certificados);
- Recorrer a JSON ou outro formato similar para estruturar as mensagens do protocolo de comunicação (eventualmente, recorrendo também a um *encoding* binário como BSON);
- Possibilitar o envio de mensagens com garantias de confidencialidade perante um servidor malicioso;
- Retirar a assumpção que o servidor é confiável para efeitos de atribuição do tempo de recepção de mensagem;
- Contemplar a existência de recibos que atestem que uma mensagem foi submetida ao sistema;
- Sistema de *Log* que registe transações do servidor;
- ...

## Relatório e material suplementar

O projecto deve ser acompanhado por um pequeno relatório que descreva o processo de desenvolvimento e documente a análise de requisitos e risco realizadas, as opções tomadas, e outra informação que considerem pertinente. Devem também ser mencionadas ferramentas que o grupo tenha adoptado durante o desenvolvimento do projecto e adicionado ao repositório o material que suportou esse uso (ficheiros de dados, etc.).
Sugere-se que este relatório seja realizado directamente em `MarkDown` acessível a partir do ficheiro `README.md` colocado na directoria do projecto no repositório do grupo (i.e. `Projs/PD1/README.md`).

