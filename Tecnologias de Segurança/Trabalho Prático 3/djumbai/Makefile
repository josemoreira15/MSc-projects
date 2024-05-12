all: directories log djumbai-group djumbai-server djumbai-user-manager djumbai-group-manager djumbai-private-manager djumbai-group-chat djumbai-private-chat djumbai-mail-server djumbai-mail-client

directories: 
	mkdir -p /usr/local/djumbai-memory/server /usr/local/djumbai-memory/users /usr/local/djumbai-memory/groups /usr/local/djumbai-memory/privates

log:
	touch /var/log/djumbai.log

djumbai-group:
	sudo groupadd djumbai

djumbai-server:
	sudo adduser djumbai-server

djumbai-user-manager:
	gcc -Wall -g src/user-manager.c src/log.c -o /usr/local/bin/djumbai-user-manager
	sudo chmod 700 /usr/local/bin/djumbai-user-manager
	sudo chown root:root /usr/local/bin/djumbai-user-manager

djumbai-group-manager:
	gcc -Wall -g src/group-manager.c src/log.c -o /usr/local/bin/djumbai-group-manager
	sudo chmod 700 /usr/local/bin/djumbai-group-manager
	sudo chown root:root /usr/local/bin/djumbai-group-manager

djumbai-private-manager:
	gcc -Wall -g src/private-manager.c src/log.c -o /usr/local/bin/djumbai-private-manager
	sudo chmod 700 /usr/local/bin/djumbai-private-manager
	sudo chown root:root /usr/local/bin/djumbai-private-manager

djumbai-group-chat:
	gcc -Wall -g src/group-chat.c src/controller.c -o /usr/local/bin/djumbai-group-chat
	sudo chgrp djumbai /usr/local/bin/djumbai-group-chat
	sudo chmod 750 /usr/local/bin/djumbai-group-chat

djumbai-private-chat:
	gcc -Wall -g src/private-chat.c src/controller.c -o /usr/local/bin/djumbai-private-chat
	sudo chgrp djumbai /usr/local/bin/djumbai-private-chat
	sudo chmod 750 /usr/local/bin/djumbai-private-chat

djumbai-mail-server:
	gcc -Wall -g src/mail-server.c src/controller.c -o /usr/local/bin/djumbai-mail-server -pthread
	sudo chgrp djumbai-server /usr/local/bin/djumbai-mail-server
	sudo chmod 750 /usr/local/bin/djumbai-mail-server

djumbai-mail-client:
	gcc -Wall -g src/mail-client.c src/controller.c -o /usr/local/bin/djumbai-mail-client
	sudo chgrp djumbai /usr/local/bin/djumbai-mail-client
	sudo chmod 750 /usr/local/bin/djumbai-mail-client

clean:
	rm -rf /usr/local/djumbai-memory
	rm /var/log/djumbai.log
	rm /usr/local/bin/djumbai-user-manager /usr/local/bin/djumbai-group-manager /usr/local/bin/djumbai-private-manager 
	rm /usr/local/bin/djumbai-group-chat /usr/local/bin/djumbai-private-chat
	sudo deluser djumbai-server
	rm -rf /home/djumbai-server
	sudo groupdel djumbai