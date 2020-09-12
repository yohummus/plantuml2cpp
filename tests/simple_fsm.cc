#include <stdio.h>

#include "out/simple_fsm.h"

int main(int argc, char *argv[])
{
    typedef SimpleFsm<>::Event Event;
    SimpleFsm<> fsm;

    fsm.init();
    printf("--- Posting JobReceived...\n");
    fsm.post_event(Event::JobReceived);
    printf("--- Posting JobDone...\n");
    fsm.post_event(Event::JobDone);

    return 0;
}
