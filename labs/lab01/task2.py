users = {
    "red_team_lead": {
        "role": "red_team",
        "clearance": 4,
        "department": "RedTeam",
        "active": True,
    },
    "blue_team_analyst": {
        "role": "blue_team",
        "clearance": 3,
        "department": "Blue Team",
        "active": True,
    },
    "purple_team_coord": {
        "role": "purple_team",
        "clearance": 3,
        "department": "Purple Team",
        "active": True,
    },
    "student_intern": {
        "role": "student",
        "clearance": 1,
        "department": "Academia",
        "active": True,
    },
    "retired_expert": {
        "role": "retired",
        "clearance": 2,
        "department": "Emeritus",
        "active": False,
    },
}
resources = [
    ("attack_scenarios", 4),
    ("defense_playbooks", 3),
    ("exercise_plans", 3),
    ("research_papers", 1),
    ("exploit_tools", 4),
    ("student_resources", 1),
    ("simulation_results", 3),
    ("red_team_tools", 4),
    ("blue_team_reports", 3),
    ("public_research", 1),
]
security_levels = ("Academic", "Operational", "Tactical", "Strategic")
blocked_users = {"retired_expert", "academic_violator", "leaked_account"}

# Вивід списку ресурсів системи
print("Список ресурсів системи \n")
for resource_name, resource_level in resources:
    level_name = security_levels[resource_level - 1]
    print(f"{resource_name}: {level_name}")


def user_status(username: str) -> str:
    """Повертає статус користувача"""

    # виключає за відсутності у списку
    if username not in users:
        return "DENY (User not found)"

    # виключає якщо користувач заблокований
    if username in blocked_users:
        return "DENY(User is blocked)"

    user_data = users[username]

    # Виключає користувача за його активністю
    if not user_data["active"]:
        return "DENY (Account inactive)"

    return "ALLOW"


def main():

    print("\nРезультат перевірки \n")
    # визначення статусу користувача
    for username in users:
        status = user_status(username)

        # алгоритм перевірки ресурсу для кожного користувача
        for resource_name, resource_level in resources:
            if status == "ALLOW":
                user_clearance = users[username]["clearance"]

                if user_clearance >= resource_level:
                    final_status = "ALLOW"
                else:
                    final_status = "DENY(Insufficient clearance)"
            else:
                final_status = status

            print(f"user=[{username}] resource=[{resource_name}] -> {final_status}")
        print()


if __name__ == "__main__":
    main()
