#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <grp.h>
#include <pwd.h>

#include "../include/private-chat.h"



int private_send(const char* user) {
    char filename[128];
    char* username = getenv("LOGNAME");

    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s-%s.txt", username, user);
    FILE* chat_file = fopen(filename, "a");

    if (chat_file == NULL) {
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s-%s.txt", user, username);
        chat_file = fopen(filename, "a");
    }

    if (chat_file != NULL) {
        char buffer[513];
        printf("[djumbai-private-chat] type your message: ");
        fgets(buffer, sizeof(buffer), stdin);

        fprintf(chat_file, "[%s] ", username);
        fprintf(chat_file, "%s", buffer);
        fclose(chat_file);

        return 0;
    }

    else {
        printf("[djumbai-private-chat] can't send a message to %s\n", user);
        return 1;
    }
}


int private_read(const char* user) {
    char filename[128];
    char* username = getenv("LOGNAME");

    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s-%s.txt", username, user);
    FILE* chat_file = fopen(filename, "r");

    if (chat_file == NULL) {
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s-%s.txt", user, username);
       chat_file = fopen(filename, "r");
    }

    if (chat_file != NULL) {
        char buffer[1024];
        while (fgets(buffer, 1024, chat_file) != NULL) {
            printf("%s", buffer);
        }

        fclose(chat_file);

        return 0;
    }

    else {
        printf("[djumbai-private-chat] can't read messages from %s\n", user);
        return 1;
    }
}


int main(int argc, char* argv[]) {
    int return_value = 0;

    if (is_member_of("djumbai")) {
        if (argc == 3) {
            if (!strcmp(argv[1], "sendprivate")) {
                return_value = private_send(argv[2]);
            }

            else if (!strcmp(argv[1], "readprivate")) {
                return_value = private_read(argv[2]);
            }

            else {
                printf("[djumbai-private-chat] invalid call\n");
                return_value = 1;
            }
        }

        else {
            printf("[djumbai-private-chat] invalid number of arguments\n");
            return_value = 1;
        }
    }

    else {
        printf("[djumbai-group-chat] can't execute without djumbaier privileges\n");
        return_value = 1;
    }

    return return_value;
}