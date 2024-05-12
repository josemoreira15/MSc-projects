#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <grp.h>
#include <pwd.h>

#include "../include/controller.h"



int is_member_of(const char* groupname) {
    int ngroups, i;
    gid_t* groups;

    ngroups = getgroups(0, NULL);
    groups = malloc(ngroups * sizeof(gid_t));
    getgroups(ngroups, groups);

    for (i = 0; i < ngroups; i++) {
        struct group* grp;
        grp = getgrgid(groups[i]);
        if (grp != NULL && !strcmp(grp->gr_name, groupname)) {
            free(groups);
            return 1;
        }
    }

    free(groups);
    return 0;
}


int is_djumbai(const char* username){
    struct group *grp;
    
    grp = getgrnam("djumbai");
    if (grp == NULL) {
        return 0;
    }
    
    for (int i = 0; grp->gr_mem[i] != NULL; i++) {
        if (strcmp(grp->gr_mem[i], username) == 0) {
            return 1;
        }
    }
    
    endgrent();
    endpwent();
    return 0;
}