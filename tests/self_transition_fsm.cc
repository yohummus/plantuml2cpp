#include <stdio.h>

#include "out/self_transition_fsm.h"

int main(int argc, char *argv[])
{
    typedef SelfTransitionFsm<>::Event Event;
    SelfTransitionFsm<> fsm;

    fsm.init();
    printf("--- Posting Timeout...\n");
    fsm.post_event(Event::Timeout);

    return 0;
}
