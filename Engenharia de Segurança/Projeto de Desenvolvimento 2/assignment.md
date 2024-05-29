# Projecto de Desenvolvimento II (PD2)

## Introdução

A expresa que encomendou o serviço de partilha de mensagens (PD1) ficou tão entusiasmada com o produto que partilhou com a empresa mãe a experiência. Essa empresa encarregou o departamento de suporte informático de tratar de adquirir um produto semelhante, mas com um âmbito alargado a todas as empresas do grupo e com requisitos que melhor se adaptassem ao novo contexto.

## Descrição

A funcionalidade básica pretendida é essencialmente a proposta para o projecto anterior (PD1), sendo que  aspectos bastante reforçados pelo departamento de suporte informático são:

 1. a ênfase não deve ser colocada na quantidade de funcionalidades oferecidas, mas antes em garantir que a funcionalidade oferecida é robusta e oferencendo as garantias de segurança descritas.
 1. deve ser preveligiada a documentação do processo de desenvolvimento, nomeadamente nos aspectos referentes à análise de risco e avaliação da segurança do produto;
 1. todos os problemas (funcionais ou de segurança) identificados na versão anterior do produto (PD1) devem ser convenientemente tratados (que inclui documentação do processo);

No entanto, e com vista à integração no ecosistema da organização, foram elencados alguns novos requisitos tecnológicos:

 * Em vez da arquitectura cliente/servidor, pretende-se uma arquitectura baseada em micro-serviços. Os diferentes comandos darão por isso origem a métodos de uma API que será responsável pelo serviço de gestão de mensagens. A sugestão é basear-se o serviço no *framework* [flask](https://flask.palletsprojects.com/), mas com liberdade para adoptar outras possibilidades como [django](https://www.djangoproject.com/); [fastAPI](https://fastapi.tiangolo.com/); ou até *frameworks* para outras linguagens como [SpingBoot](https://spring.io/projects/spring-boot) para Java; etc.
 * Dado que o JSON será implicitamente adoptado na interacção com a API, sugere-se que também a funcionalidade criptográfica do serviço adopte esse mesmo formato recorrendo a [Javascript Object Signing and Encryption](https://datatracker.ietf.org/wg/jose/about/).
 * Ao nível da autenticação dos utilizadores, a solução baseada no TLS suscita dúvidas. A ser mantida, deve ser objecto de um escrutínio particular que explicite as assumpções e garantias associadas. Em alternativa, propõe-se a adopção de um mecanismo de autenticação federativa baseado num *standard* estabelecido, como o **OpenID Connect (OIDC)** (mas também aqui se admite a adopção de outras soluções como a utilização de autenticação baseada em **JSON Web Tokes (JWT)**).

## Apontadores

### *frameworks*

 * https://kinsta.com/blog/flask-vs-django/
 * https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
 * https://flask.palletsprojects.com/en/3.0.x/
 * https://click.palletsprojects.com/en/8.1.x/

<!-->
 * https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
 * https://www.codemotion.com/magazine/microservices/microservices-python/
<-->


### JSON; JWT; JOSE

 * https://medium.com/apinizer/jose-json-object-signing-and-encryption-framework-aeefcf27775
 * https://www.scottbrady91.com/jose/json-web-encryption

### Autenticação e Autorização

 * https://www.keycloak.org/
 * https://curity.io/product/community/
 * https://docs.authlib.org/en/latest/
 * https://auth0.com/docs/quickstart/backend/python
 * https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask-in-2023
 * https://gist.github.com/nebulak/6d865ddd768fb905a562d6026cdd508a; https://github.com/stef/flask-tlsauth; https://stackoverflow.com/questions/76328989/user-authentication-using-a-certificate-x-509-in-python-with-flask-on-windows-10

