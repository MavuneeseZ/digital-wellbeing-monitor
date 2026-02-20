def detect_conflicts(entries):
    conflicts = []

    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):

            a = entries[i]
            b = entries[j]

            if a.day == b.day and a.slot == b.slot:

                if a.teacher == b.teacher:
                    conflicts.append({
                        "type": "Teacher Conflict",
                        "message": f"{a.teacher} double booked at {a.day} {a.slot}"
                    })

                if a.room == b.room:
                    conflicts.append({
                        "type": "Room Conflict",
                        "message": f"{a.room} double booked at {a.day} {a.slot}"
                    })

                if a.class_name == b.class_name:
                    conflicts.append({
                        "type": "Class Conflict",
                        "message": f"{a.class_name} has 2 classes at {a.day} {a.slot}"
                    })

    return conflicts
