import pytest
import sqlite3
from pathlib import Path
from click.testing import CliRunner
from my_cli import cli, init_db, DB_FILE
from datetime import datetime

@pytest.fixture
def runner():
    """Fixture que proporciona un runner de Click para pruebas"""
    return CliRunner()

@pytest.fixture
def test_db(monkeypatch):
    """Fixture que crea una base de datos temporal para pruebas"""
    # Usar una base de datos temporal para pruebas
    test_db_file = Path('test_tasks.db')
    
    # Asegurarse de que empezamos con una base de datos limpia
    if test_db_file.exists():
        test_db_file.unlink()
    
    # Usar monkeypatch para modificar la ruta de la base de datos
    monkeypatch.setattr('my_cli.DB_FILE', test_db_file)
    
    # Inicializar la base de datos de prueba
    init_db()
    
    yield test_db_file
    
    # Limpiar después de las pruebas
    if test_db_file.exists():
        test_db_file.unlink()

def test_add_task(runner, test_db):
    """Prueba la funcionalidad de agregar tareas"""
    # Agregar una tarea simple
    result = runner.invoke(cli, ['add', 'Hacer compras', '-p', '3'])
    assert result.exit_code == 0
    assert 'Tarea agregada: Hacer compras' in result.output
    
    # Verificar que la tarea se guardó en la base de datos
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('SELECT description, priority, completed FROM tasks')
    task = c.fetchone()
    conn.close()
    
    assert task[0] == 'Hacer compras'
    assert task[1] == 3
    assert task[2] == 0  # no completada

def test_add_task_invalid_priority(runner, test_db):
    """Prueba agregar una tarea con prioridad inválida"""
    result = runner.invoke(cli, ['add', 'Tarea inválida', '-p', '6'])
    assert result.exit_code == 0
    assert 'La prioridad debe estar entre 1 y 5' in result.output

def test_list_tasks(runner, test_db):
    """Prueba listar tareas"""
    # Agregar algunas tareas de prueba
    runner.invoke(cli, ['add', 'Tarea 1', '-p', '1'])
    runner.invoke(cli, ['add', 'Tarea 2', '-p', '3'])
    
    # Probar listado normal
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Tarea 1' in result.output
    assert 'Tarea 2' in result.output
    
    # Probar listado por prioridad
    result = runner.invoke(cli, ['list', '-p'])
    assert result.exit_code == 0
    # La Tarea 2 (prioridad 3) debe aparecer antes que la Tarea 1 (prioridad 1)
    assert result.output.index('Tarea 2') < result.output.index('Tarea 1')

def test_list_empty(runner, test_db):
    """Prueba listar cuando no hay tareas"""
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'No hay tareas pendientes' in result.output

def test_delete_task(runner, test_db):
    """Prueba eliminar una tarea desde cualquier posición"""
    # Agregar varias tareas
    runner.invoke(cli, ['add', 'Tarea 1', '-p', '1'])
    runner.invoke(cli, ['add', 'Tarea para eliminar', '-p', '2'])
    runner.invoke(cli, ['add', 'Tarea 3', '-p', '3'])
    
    # Obtener el ID de la tarea del medio
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('SELECT id FROM tasks WHERE description = ?', ('Tarea para eliminar',))
    task_id = c.fetchone()[0]
    conn.close()
    
    # Eliminar la tarea
    result = runner.invoke(cli, ['delete', str(task_id)])
    assert result.exit_code == 0
    assert f'Tarea eliminada con ID: {task_id}' in result.output
    
    # Verificar que solo se eliminó la tarea correcta
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('SELECT description FROM tasks ORDER BY id')
    remaining_tasks = c.fetchall()
    conn.close()
    
    assert len(remaining_tasks) == 2
    assert ('Tarea 1',) in remaining_tasks
    assert ('Tarea 3',) in remaining_tasks
    assert ('Tarea para eliminar',) not in remaining_tasks

def test_delete_invalid_task(runner, test_db):
    """Prueba eliminar una tarea que no existe"""
    result = runner.invoke(cli, ['delete', '999'])
    assert result.exit_code == 0
    assert 'ID de tarea inválido' in result.output

def test_complete_task(runner, test_db):
    """Prueba marcar como completada una tarea desde cualquier posición"""
    # Agregar varias tareas
    runner.invoke(cli, ['add', 'Tarea 1', '-p', '1'])
    runner.invoke(cli, ['add', 'Tarea para completar', '-p', '2'])
    runner.invoke(cli, ['add', 'Tarea 3', '-p', '3'])
    
    # Obtener el ID de la tarea del medio
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('SELECT id FROM tasks WHERE description = ?', ('Tarea para completar',))
    task_id = c.fetchone()[0]
    conn.close()
    
    # Completar la tarea
    result = runner.invoke(cli, ['complete', str(task_id)])
    assert result.exit_code == 0
    assert f'Tarea completada con ID: {task_id}' in result.output
    
    # Verificar que solo la tarea correcta está marcada como completada
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute('SELECT description, completed FROM tasks ORDER BY id')
    tasks_status = c.fetchall()
    conn.close()
    
    assert len(tasks_status) == 3
    for description, completed in tasks_status:
        if description == 'Tarea para completar':
            assert completed == 1
        else:
            assert completed == 0

def test_complete_invalid_task(runner, test_db):
    """Prueba completar una tarea que no existe"""
    result = runner.invoke(cli, ['complete', '999'])
    assert result.exit_code == 0
    assert 'ID de tarea inválido' in result.output

def test_list_sort_by_creation(runner, test_db):
    """Prueba listar tareas ordenadas por fecha de creación"""
    # Agregar tareas en orden específico
    runner.invoke(cli, ['add', 'Tarea más antigua', '-p', '1'])
    runner.invoke(cli, ['add', 'Tarea más reciente', '-p', '5'])
    
    # Verificar orden por fecha de creación
    result = runner.invoke(cli, ['list', '-c'])
    assert result.exit_code == 0
    assert result.output.index('Tarea más antigua') < result.output.index('Tarea más reciente')