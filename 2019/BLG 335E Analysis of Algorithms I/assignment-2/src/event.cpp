/* @Author
* Student Name: Şahin Akkaya
* Student ID : 150170098
* Date: 11.12.2019 */


#include "event.h"

Event::Event(string event_name, int event_time, string event_type) 
{ 
    this->event_name = event_name;
    this->event_time = event_time;
    this->event_type = event_type;
}


string Event::get_event_name(){
    return event_name;
} 
        
int Event::get_event_time(){
    return event_time;
}


string Event::get_event_type(){
    return event_type;
} 
