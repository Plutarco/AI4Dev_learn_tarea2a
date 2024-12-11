import pytest
from click.testing import CliRunner
import json
from pathlib import Path
from my_cli import cli, TASKS_FILE

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def clean_tasks_file():
    """Limpia el archivo de tareas antes y después de cada prueba"""
    if TASKS_FILE.exists():
        TASKS_FILE.unlink()
    yield
    if TASKS_FILE.exists():
        TASKS_FILE.unlink()

def test_add_task(runner, clean_tasks_file):
    """Prueba agregar una nueva tarea"""
    result = runner.invoke(cli, ['add', 'Test task', '-p', '3'])
    assert result.exit_code == 0
    assert "Tarea agregada: Test task" in result.output
    
    # Verifica que la tarea se guardó correctamente
    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)
    assert len(tasks) == 1
    assert tasks[0]['description'] == 'Test task'
    assert tasks[0]['priority'] == 3

def test_list_tasks(runner, clean_tasks_file):
    """Prueba listar tareas"""
    # Agrega algunas tareas de prueba
    runner.invoke(cli, ['add', 'Task 1', '-p', '1'])
    runner.invoke(cli, ['add', 'Task 2', '-p', '3'])
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "Task 1" in result.output
    assert "Task 2" in result.output

def test_delete_task(runner, clean_tasks_file):
    """Prueba eliminar una tarea"""
    runner.invoke(cli, ['add', 'Task to delete', '-p', '1'])
    result = runner.invoke(cli, ['delete', '1'])
    assert result.exit_code == 0
    assert "Tarea eliminada" in result.output

def test_complete_task(runner, clean_tasks_file):
    """Prueba marcar una tarea como completada"""
    runner.invoke(cli, ['add', 'Task to complete', '-p', '1'])
    result = runner.invoke(cli, ['complete', '1'])
    assert result.exit_code == 0
    assert "Tarea completada" in result.output

def test_list_by_priority(runner, clean_tasks_file):
    """Prueba listar tareas ordenadas por prioridad"""
    runner.invoke(cli, ['add', 'Low priority', '-p', '1'])
    runner.invoke(cli, ['add', 'High priority', '-p', '5'])
    
    result = runner.invoke(cli, ['list', '-p'])
    assert result.exit_code == 0
    # Verifica que la tarea de alta prioridad aparece primero
    assert result.output.index('High priority') < result.output.index('Low priority') 

def test_sequence_of_operations(runner, clean_tasks_file):
    """Prueba una secuencia específica de operaciones con tareas"""
    # Añadir 4 tareas de ejemplo
    tasks_to_add = [
        ('Hacer compras', 2),
        ('Llamar al médico', 3),
        ('Pagar facturas', 1),
        ('Preparar presentación', 4)
    ]
    
    # Agregar las tareas
    for description, priority in tasks_to_add:
        result = runner.invoke(cli, ['add', description, '-p', str(priority)])
        assert result.exit_code == 0
        assert f"Tarea agregada: {description}" in result.output
    
    # Verificar que se agregaron las 4 tareas
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    for description, _ in tasks_to_add:
        assert description in result.output
    
    # Eliminar la segunda tarea
    result = runner.invoke(cli, ['delete', '2'])
    assert result.exit_code == 0
    assert "Tarea eliminada: Llamar al médico" in result.output
    
    # Verificar que la tarea se eliminó
    result = runner.invoke(cli, ['list'])
    assert "Llamar al médico" not in result.output
    
    # Marcar como completada la tercera tarea (que ahora es la segunda después de eliminar)
    result = runner.invoke(cli, ['complete', '2'])
    assert result.exit_code == 0
    assert "Tarea completada: Pagar facturas" in result.output
    
    # Verificar que la tarea está marcada como completada
    result = runner.invoke(cli, ['list'])
    assert "[✓] Pagar facturas" in result.output
    
    # Eliminar la tercera tarea (que ahora es la segunda después de eliminar)
    result = runner.invoke(cli, ['delete', '2'])
    assert result.exit_code == 0
    assert "Tarea eliminada: Pagar facturas" in result.output
    
    # Verificar el estado final
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "Hacer compras" in result.output
    assert "Preparar presentación" in result.output
    assert "Llamar al médico" not in result.output
    assert "Pagar facturas" not in result.output