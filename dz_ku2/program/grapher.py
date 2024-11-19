import subprocess
import argparse
from datetime import datetime


def get_commits(repo_path, date_filter):
    try:
        log_format = "%H|%P|%an|%ad|%s"
        git_command = [
            "git", "-C", repo_path, "log",
            "--all", f"--before={date_filter}",
            f"--pretty=format:{log_format}", "--date=iso"
        ]
        result = subprocess.run(git_command, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении git log: {e}")
        return []


def parse_commits(commits):
    parsed = []
    for commit in commits:
        parts = commit.split('|')
        parsed.append({
            "hash": parts[0],
            "parents": parts[1].split() if parts[1] else [],
            "author": parts[2],
            "date": parts[3],
            "message": parts[4]
        })
    return parsed


def build_mermaid_graph(commits):
    lines = ["graph TD"]
    nodes = {}

    for commit in commits:
        node_id = commit["hash"][:7]
        node_label = f'{commit["message"]}<br>{commit["date"]}<br>Автор: {commit["author"]}'
        nodes[commit["hash"]] = f'{node_id}["{node_label}"]'

    for commit in commits:
        current_node = nodes[commit["hash"]]
        lines.append(f'    {current_node}')
        for parent in commit["parents"]:
            if parent in nodes:
                lines.append(f'    {current_node} --> {nodes[parent]}')

    return "\n".join(lines)


def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей Git.")
    parser.add_argument("--repo-path", required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output-file", required=True, help="Путь к файлу-результату в виде кода.")
    parser.add_argument("--date", required=True, help="Дата коммитов в репозитории.")

    args = parser.parse_args()

    commits = get_commits(args.repo_path, args.date)
    if not commits:
        print("Нет подходящих коммитов.")
        return

    parsed_commits = parse_commits(commits)

    graph = build_mermaid_graph(parsed_commits)

    write_to_file(args.output_file, graph)
    print(f"Граф записан в файл {args.output_file}")


if __name__ == "__main__":
    main()
