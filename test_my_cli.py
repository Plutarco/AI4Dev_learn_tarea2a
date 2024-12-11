import pytest
from click.testing import CliRunner
import sys
from my_cli import cli

def test_version_command():
    """Prueba que el comando version muestre la versión correcta de Python"""
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    
    # Verifica que el comando se ejecutó exitosamente
    assert result.exit_code == 0
    
    # Obtiene la versión esperada de Python
    expected_version = sys.version.split()[0]
    
    # Verifica que la salida contiene la versión correcta
    assert f"Python versión: {expected_version}" in result.output

def test_help_command():
    """Prueba que el comando help funcione correctamente"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    
    # Verifica que el comando se ejecutó exitosamente
    assert result.exit_code == 0
    
    # Verifica que la salida contiene información esperada
    assert "Una herramienta CLI simple" in result.output
    assert "version" in result.output 