#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "../include/mail-client.h"

#define FIRST_LOG 3
#define SEND_MSG 1
#define REQUEST_MSG 2



int send_struct(int* arg, my_message m){
    int socket = *((int *)arg);
    char buffer[BUFFER_SIZE] = {0};
    int nbytes;
    if ((nbytes = write(socket, &m, sizeof(my_message)) != sizeof(my_message))){
        printf("[djumbai-client] error writing my message\n");
    }

    read(socket, buffer, BUFFER_SIZE);
    printf("[djumbai-mail-client] %s\n", buffer);
    memset(buffer, 0, BUFFER_SIZE);

    return 0;
}


int request_email(int* arg, my_message m){
    int socket = *((int *)arg);
    char buffer[BUFFER_SIZE] = {0};
    long file_size;
    int nbytes, n;
    if ((nbytes = write(socket, &m, sizeof(my_message)) != sizeof(my_message))){
        printf("[djumbai-client] error writing my message\n");
    }

    if (read(socket, &file_size, sizeof(file_size)) < 0) {
        return 1;
    }

    char filename[128];
    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/users/%s.txt", m.user);

    FILE* file = fopen(filename, "a");
    while (file_size > 0) {
        n = read(socket, buffer, sizeof(buffer));
        if (n < 0) {
            return 1;
        }
        printf("%.*s", n, buffer);
        fwrite(buffer, 1, n, file);
        file_size -= n;
    }

    return 0;
}


int main(int argc, char* argv[]) {
    if (is_member_of("djumbai")) {
        int sock = 0;
        struct sockaddr_in serv_addr;
        size_t len;

        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            return 1;
        }

        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(PORT);


        if (inet_pton(AF_INET, "127.0.0.2", &serv_addr.sin_addr) <= 0) {
            return 1;
        }

        if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
            return 1;
        }

        my_message m;

        strcpy(m.target, "default-user");
        int *arg = malloc(sizeof(*arg));
        if (arg == NULL) {
            return 1;
        }

        *arg = sock;
        char *username = getenv("LOGNAME");
        strcpy(m.user, username);

        if (argc == 3 && !strcmp(argv[1], "sendmail")) {
            m.message_type = 1;
            strcpy(m.target, argv[2]);
            printf("[djumbai-mail-client] type your message: ");
            fgets(m.buff, sizeof(m.buff), stdin);
            len = strcspn(m.buff, "\n");
            if (m.buff[len] == '\n') {
                m.buff[len] = '\0';
            }
            send_struct(arg, m);
        }

        else if (argc == 2 && !strcmp(argv[1], "readmails")) {
            m.message_type = 2;
            strcpy(m.buff,"default-msg");
            request_email(arg, m);
        }

        else {
            printf("[djumbai-mail-client] invalid arguments\n");
        }
    }

    else {
        printf("[djumbai-mail-client] can't execute without djumbaier privileges\n");
        return 1;
    }

    return 0;
}