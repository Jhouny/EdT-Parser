import uuid

class Event:
    def __init__(self, title, start_time, end_time, location=None, description=None):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.description = description
        # ID is a unique identifier for the event, useful for hashing and equality checks
        # --> It is derived from the title, start_time, and end_time to ensure uniqueness
        self.event_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{title}-{start_time}-{end_time}"))
    
    def __repr__(self):
        return f"Event(title={self.title}, start_time={self.start_time}, end_time={self.end_time}, location={self.location}, description={self.description}, event_id={self.event_id})"
    
    def __eq__(self, other):
        """Two events are equal if they have the same event_id"""
        if not isinstance(other, Event):
            return False
        return self.event_id == other.event_id
    
    def __hash__(self):
        """Use event_id for hashing so events can be used as dictionary keys"""
        return hash(self.event_id)
    
    def duration(self):
        return self.end_time - self.start_time
    
    def overlaps(self, other_event):
        return self.start_time < other_event.end_time and self.end_time > other_event.start_time