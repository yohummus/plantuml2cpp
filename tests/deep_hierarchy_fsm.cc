#include <stdio.h>

#include "out/deep_hierarchy_fsm.h"

int main(int argc, char *argv[])
{
    typedef DeepHierarchyFsm<>::Event Event;
    DeepHierarchyFsm<> fsm;

    fsm.init();
    printf("--- Posting New4kMonitorArrived...\n");
    fsm.post_event(Event::New4kMonitorArrived);
    printf("--- Posting HeardSomeNoise...\n");
    fsm.post_event(Event::HeardSomeNoise);
    printf("--- Posting SawSomething...\n");
    fsm.post_event(Event::SawSomething);
    printf("--- Posting Glitch...\n");
    fsm.post_event(Event::Glitch);
    printf("--- Posting Timeout...\n");
    fsm.post_event(Event::Timeout);
    printf("--- Posting HeardSomething...\n");
    fsm.post_event(Event::HeardSomething);

    return 0;
}
