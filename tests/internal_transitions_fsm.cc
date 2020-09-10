#include <stdio.h>

#include "out/internal_transitions_fsm.h"

int main(int argc, char *argv[])
{
    typedef InternalTransitionsFsm<>::Event Event;
    InternalTransitionsFsm<> fsm;

    fsm.init();
    printf("--- Posting GotHungry...\n");
    fsm.post_event(Event::GotHungry);
    printf("--- Posting HitSomething...\n");
    fsm.post_event(Event::HitSomething);

    return 0;
}
