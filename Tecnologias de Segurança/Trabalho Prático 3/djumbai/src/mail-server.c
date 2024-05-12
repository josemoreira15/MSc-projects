#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <asm-generic/socket.h>
#include <bits/pthreadtypes.h>
#include <pthread.h>
#include <pwd.h>
#include <sys/stat.h>
#include <grp.h>

#include "../include/mail-server.h"

#define FIRST_LOG 1
#define SEND_MSG 2
#define REQUEST_MSG 3



int send_email(my_message message, void* arg, pthread_mutex_t mutex1){
    const char *response = "message sent";
    int socket = *((int *)arg);
    pthread_mutex_lock( &mutex1 );
    FILE *fp;
    char filename[128];
    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/server/%s.txt", message.target);
    
    fp = fopen(filename, "a+");
    fprintf(fp, "[%s] %s\n", message.user, message.buff);
    fclose(fp);
    pthread_mutex_unlock(&mutex1);
    
    send(socket, response, strlen(response), 0);
    return 0;
}


int request_email(my_message message, void* arg, pthread_mutex_t mutex1){
    int socket = *((int *)arg);
    long file_size;
    int n;
    char buffer[BUFFER_SIZE];
    FILE *fp;
    char filename[128];
    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/server/%s.txt", message.user);
    
    fp = fopen(filename, "r");
    fseek(fp, 0, SEEK_END);
    file_size = ftell(fp);
    rewind(fp);

    n = write(socket, &file_size, sizeof(file_size));
    if (n < 0) {
        return 1;
    }


    while ((n = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        if (write(socket, buffer, n) < 0) {
            return 1;
        }
    }

    fclose(fp);
    fp = fopen(filename, "w");
    fclose(fp);
    
    return 0;
}


void* handle_client(void* arg) {
    pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
    int new_socket = *((int *)arg);
    const char* negative_response = "can't send a message to that user";
    
    my_message received_message;
    int size;

    if ((size = recv( new_socket, (void*)&received_message, sizeof(my_message), 0)) >= 0) {}
        
    if (received_message.message_type == 1){
        if(is_djumbai(received_message.target)){
            send_email(received_message, arg, mutex1);
        }
            
        else {
            send(new_socket, negative_response, strlen(negative_response), 0);
        }
    }
        
    else if(received_message.message_type == 2){
        pthread_mutex_lock(&mutex1);
        pthread_mutex_unlock(&mutex1);
        request_email(received_message, arg, mutex1);
    }
    
    close(new_socket);
    free(arg);

    return NULL;
}


int main(int argc, char* argv[]) {
    if (argc == 1) {
        if (is_member_of("djumbai-server")) {
            int server_fd, new_socket;
            struct sockaddr_in address;
            int addrlen = sizeof(address);
            pthread_t thread;

            if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
                return 1;
            }

            if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &(int){1}, sizeof(int)) < 0) {
                return 1;
            }

            address.sin_family = AF_INET;
            address.sin_addr.s_addr = INADDR_ANY;
            address.sin_port = htons(PORT);

            if (bind(server_fd, (struct sockaddr *)&address, sizeof(address))<0) {
                return 1;
            }
            if (listen(server_fd, 3) < 0) {
                return 1;
            }

            while (1) {
                if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen))<0) {
                    return 1;
                }

                int *arg = malloc(sizeof(*arg));
                if (arg == NULL) {
                    return 1;
                }

                *arg = new_socket;

                if (pthread_create(&thread, NULL, handle_client, arg) != 0) {
                    free(arg);
                    return 1;
                }
            }
        }

        else {
            printf("[djumbai-mail-server] only djumbai-server can execute\n");
            return 1;
        }
    }

    else {
        printf("[djumbai-mail-server] invalid number of arguments\n");
        return 1;
    }

    return 0;
}