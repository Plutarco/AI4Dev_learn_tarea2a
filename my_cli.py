""" Sistema CLI de ToDo List 
Este sistema es una herramienta CLI para gestionar una lista de tareas pendientes.
Tiene los siguientes comandos:

- add: Agrega una nueva tarea junto con su prioridad a la lista.
- list: Muestra todas las tareas pendientes.
    opción -p: Muestra las tareas ordenadas por prioridad.
    opción -c: Muestra las tareas ordenadas por fecha de creación.
- delete: Elimina una tarea existente de la lista.
- complete: Marca una tarea como completada.
"""
import click
import sys
from datetime import datetime
import json
from pathlib import Path

# Archivo para almacenar las tareas
TASKS_FILE = Path('tasks.json')

def load_tasks():
    """Carga las tareas desde el archivo JSON"""
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Guarda las tareas en el archivo JSON"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@click.group()
def cli():
    """Sistema CLI para gestionar una lista de tareas pendientes"""
    pass

@cli.command()
@click.argument('description')
@click.option('-p', '--priority', type=int, default=1, help='Prioridad de la tarea (1-5)')
def add(description, priority):
    """Agrega una nueva tarea con su prioridad"""
    if not 1 <= priority <= 5:
        click.echo("La prioridad debe estar entre 1 y 5")
        return
    
    tasks = load_tasks()
    task = {
        'description': description,
        'priority': priority,
        'created_at': datetime.now().isoformat(),
        'completed': False
    }
    tasks.append(task)
    save_tasks(tasks)
    click.echo(f"Tarea agregada: {description}")

@cli.command()
@click.option('-p', '--by-priority', is_flag=True, help='Ordenar por prioridad')
@click.option('-c', '--by-creation', is_flag=True, help='Ordenar por fecha de creación')
def list(by_priority, by_creation):
    """Muestra todas las tareas pendientes"""
    tasks = load_tasks()
    
    if by_priority:
        tasks.sort(key=lambda x: x['priority'], reverse=True)
    elif by_creation:
        tasks.sort(key=lambda x: x['created_at'])
    
    if not tasks:
        click.echo("No hay tareas pendientes")
        return
    
    for i, task in enumerate(tasks, 1):
        status = "✓" if task['completed'] else " "
        click.echo(f"{i}. [{status}] {task['description']} (Prioridad: {task['priority']})")

@cli.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Elimina una tarea existente por su ID"""
    tasks = load_tasks()
    if not 1 <= task_id <= len(tasks):
        click.echo("ID de tarea inválido")
        return
    
    deleted_task = tasks.pop(task_id - 1)
    save_tasks(tasks)
    click.echo(f"Tarea eliminada: {deleted_task['description']}")

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Marca una tarea como completada por su ID"""
    tasks = load_tasks()
    if not 1 <= task_id <= len(tasks):
        click.echo("ID de tarea inválido")
        return
    
    tasks[task_id - 1]['completed'] = True
    save_tasks(tasks)
    click.echo(f"Tarea completada: {tasks[task_id - 1]['description']}")

if __name__ == '__main__':
    cli()
