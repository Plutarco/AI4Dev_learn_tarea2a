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
import sqlite3
from pathlib import Path

# Archivo de la base de datos
DB_FILE = Path('tasks.db')

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            priority INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def load_tasks():
    """Carga las tareas desde la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = [{
        'id': row[0],
        'description': row[1],
        'priority': row[2],
        'created_at': row[3],
        'completed': bool(row[4])
    } for row in c.fetchall()]
    conn.close()
    return tasks

def save_task(description, priority, created_at):
    """Guarda una nueva tarea en la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (description, priority, created_at, completed)
        VALUES (?, ?, ?, ?)
    ''', (description, priority, created_at, False))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Elimina una tarea de la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def complete_task(task_id):
    """Marca una tarea como completada en la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

@click.group()
def cli():
    """Sistema CLI para gestionar una lista de tareas pendientes"""
    init_db()  # Aseguramos que la base de datos existe
    pass

@cli.command()
@click.argument('description')
@click.option('-p', '--priority', type=int, default=1, help='Prioridad de la tarea (1-5)')
def add(description, priority):
    """Agrega una nueva tarea con su prioridad"""
    if not 1 <= priority <= 5:
        click.echo("La prioridad debe estar entre 1 y 5")
        return
    
    save_task(description, priority, datetime.now().isoformat())
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
    
    for task in tasks:
        status = "✓" if task['completed'] else " "
        click.echo(f"{task['id']}. [{status}] {task['description']} (Prioridad: {task['priority']})")

@cli.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Elimina una tarea existente por su ID"""
    tasks = load_tasks()
    task_exists = any(task['id'] == task_id for task in tasks)
    
    if not task_exists:
        click.echo("ID de tarea inválido")
        return
    
    delete_task(task_id)
    click.echo(f"Tarea eliminada con ID: {task_id}")

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Marca una tarea como completada por su ID"""
    tasks = load_tasks()
    task_exists = any(task['id'] == task_id for task in tasks)
    
    if not task_exists:
        click.echo("ID de tarea inválido")
        return
    
    complete_task(task_id)
    click.echo(f"Tarea completada con ID: {task_id}")

if __name__ == '__main__':
    cli()
