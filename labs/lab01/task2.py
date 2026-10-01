from rich.console import Console
from rich.table import Table

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
    
    console = Console()

    # Таблиця ресурсів системи
    res_table = Table(title="Список ресурсів системи")
    res_table.add_column("Ресурс", style="white", no_wrap=True)
    res_table.add_column("Рівень безпеки", style="magenta", justify="center")

    for resource_name, resource_level in resources:
        level_name = security_levels[resource_level - 1]
        res_table.add_row(resource_name, level_name)

    console.print(res_table)
    console.print()

    # Таблиця результатів перевірки доступу
    access_table = Table(title="Результати перевірки доступу")
    access_table.add_column("Користувач")
    access_table.add_column("Ресурс", style="white")
    access_table.add_column("Рівень ресурсу", style="magenta", justify="center")
    access_table.add_column("Статус доступу", justify="center")

    # визначення статусу користувача
    for username in users:
        status = user_status(username)

        for resource_name, resource_level in resources:
            level_name = security_levels[resource_level - 1]
            
            if status == "ALLOW":
                user_clearance = users[username]["clearance"]
                if user_clearance >= resource_level:
                    final_status = "ALLOW"
                    color = "green"
                else:
                    final_status = "DENY (Insufficient clearance)"
                    color = "red"
            else:
                final_status = status
                color = "red"

            access_table.add_row(
                username, 
                resource_name, 
                level_name, 
                f"[{color}]{final_status}[/{color}]"
            )

    console.print(access_table)




if __name__ == "__main__":
    main()
