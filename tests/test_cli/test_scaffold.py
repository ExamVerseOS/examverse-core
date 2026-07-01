"""Tests for ``examverse scaffold`` — full scaffolding engine."""

from __future__ import annotations

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from examverse_core.cli.main import app

runner = CliRunner()


# ── helpers ────────────────────────────────────────────────────────────────────

def _preview(args: list[str]) -> str:
    """Invoke a scaffold command with --preview and return output."""
    result = runner.invoke(app, ["scaffold"] + args + ["--preview"])
    assert result.exit_code == 0, f"Exit {result.exit_code}: {result.output}"
    return result.output


def _write(args: list[str], tmp: Path) -> dict[str, str]:
    """Invoke a scaffold command writing to *tmp*, return {rel_path: content}."""
    result = runner.invoke(app, ["scaffold"] + args + ["--out-dir", str(tmp)])
    assert result.exit_code == 0, f"Exit {result.exit_code}: {result.output}"
    return {
        str(p.relative_to(tmp)): p.read_text()
        for p in tmp.rglob("*")
        if p.is_file()
    }


# ── scaffold event ─────────────────────────────────────────────────────────────

class TestScaffoldEvent:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert out  # something printed

    def test_preview_contains_event_class(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "UserRegistered" in out

    def test_preview_contains_handler(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "UserRegisteredHandler" in out

    def test_preview_contains_subscription(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "register" in out

    def test_preview_contains_tests(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "pytest" in out

    def test_preview_contains_docs(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "## Overview" in out or "Event Schema" in out

    def test_preview_shows_correlation_id(self) -> None:
        out = _preview(["event", "UserRegistered"])
        assert "correlation_id" in out

    def test_write_creates_five_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert len(files) == 5

    def test_write_creates_event_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert any("events" in k and "user_registered.py" in k for k in files)

    def test_write_creates_handler_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert any("handler" in k for k in files)

    def test_write_creates_subscription_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert any("subscription" in k for k in files)

    def test_write_creates_test_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert any("test_" in k for k in files)

    def test_write_creates_docs_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        assert any(k.endswith(".md") for k in files)

    def test_event_file_has_domain_event_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        event_content = next(v for k, v in files.items() if "events" in k and k.endswith(".py"))
        assert "DomainEvent" in event_content

    def test_event_file_has_google_docstring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        event_content = next(v for k, v in files.items() if "events" in k and k.endswith(".py"))
        assert "Args:" in event_content or "Attributes:" in event_content or '"""' in event_content

    def test_event_file_has_type_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        event_content = next(v for k, v in files.items() if "events" in k and k.endswith(".py"))
        assert "str" in event_content

    def test_test_file_has_immutability_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        test_content = next(v for k, v in files.items() if "test_" in k)
        assert "immutable" in test_content or "frozen" in test_content or "pytest.raises" in test_content

    def test_docs_file_has_event_schema_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered"], Path(tmp))
        docs_content = next(v for k, v in files.items() if k.endswith(".md"))
        assert "correlation_id" in docs_content
        assert "version" in docs_content

    def test_hyphenated_name(self) -> None:
        out = _preview(["event", "exam-submitted"])
        assert "ExamSubmitted" in out

    def test_version_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["event", "UserRegistered", "--version", "2"], Path(tmp))
        test_content = next(v for k, v in files.items() if "test_" in k)
        assert "2" in test_content


# ── scaffold aggregate ─────────────────────────────────────────────────────────

class TestScaffoldAggregate:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["aggregate", "Order"])
        assert out

    def test_generates_aggregate_root(self) -> None:
        out = _preview(["aggregate", "Order"])
        assert "AggregateRoot" in out or "Order" in out

    def test_generates_domain_event(self) -> None:
        out = _preview(["aggregate", "Order"])
        assert "OrderCreated" in out or "DomainEvent" in out

    def test_generates_factory_method(self) -> None:
        out = _preview(["aggregate", "Order"])
        assert "create" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["aggregate", "Order"], Path(tmp))
        assert len(files) == 1


# ── scaffold model ─────────────────────────────────────────────────────────────

class TestScaffoldModel:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["model", "UserProfile"])
        assert out

    def test_generates_pydantic_model(self) -> None:
        out = _preview(["model", "UserProfile"])
        assert "BaseModel" in out

    def test_has_frozen_config(self) -> None:
        out = _preview(["model", "UserProfile"])
        assert "frozen" in out

    def test_has_uuid_id(self) -> None:
        out = _preview(["model", "UserProfile"])
        assert "UUID" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["model", "UserProfile"], Path(tmp))
        assert len(files) == 1


# ── scaffold command ───────────────────────────────────────────────────────────

class TestScaffoldCommand:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["command", "RegisterUser"])
        assert out

    def test_generates_command_class(self) -> None:
        out = _preview(["command", "RegisterUser"])
        assert "RegisterUser" in out

    def test_generates_handler(self) -> None:
        out = _preview(["command", "RegisterUser"])
        assert "RegisterUserHandler" in out

    def test_has_correlation_id(self) -> None:
        out = _preview(["command", "RegisterUser"])
        assert "correlation_id" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["command", "RegisterUser"], Path(tmp))
        assert len(files) == 1


# ── scaffold query ─────────────────────────────────────────────────────────────

class TestScaffoldQuery:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["query", "GetUserById"])
        assert out

    def test_generates_query_class(self) -> None:
        out = _preview(["query", "GetUserById"])
        assert "GetUserById" in out

    def test_generates_result_class(self) -> None:
        out = _preview(["query", "GetUserById"])
        assert "GetUserByIdResult" in out

    def test_generates_handler(self) -> None:
        out = _preview(["query", "GetUserById"])
        assert "GetUserByIdHandler" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["query", "GetUserById"], Path(tmp))
        assert len(files) == 1


# ── scaffold provider ──────────────────────────────────────────────────────────

class TestScaffoldProvider:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["provider", "OpenAILLM"])
        assert out

    def test_generates_llm_provider(self) -> None:
        out = _preview(["provider", "OpenAILLM"])
        assert "LLMProvider" in out

    def test_has_complete_method(self) -> None:
        out = _preview(["provider", "OpenAILLM"])
        assert "complete" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["provider", "OpenAILLM"], Path(tmp))
        assert len(files) == 1


# ── scaffold worker ────────────────────────────────────────────────────────────

class TestScaffoldWorker:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["worker", "EmailDispatch"])
        assert out

    def test_generates_worker_class(self) -> None:
        out = _preview(["worker", "EmailDispatch"])
        assert "EmailDispatchWorker" in out

    def test_has_start_stop(self) -> None:
        out = _preview(["worker", "EmailDispatch"])
        assert "start" in out and "stop" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["worker", "EmailDispatch"], Path(tmp))
        assert len(files) == 1


# ── scaffold scheduler ─────────────────────────────────────────────────────────

class TestScaffoldScheduler:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["scheduler", "DailyReport"])
        assert out

    def test_generates_task_class(self) -> None:
        out = _preview(["scheduler", "DailyReport"])
        assert "DailyReportTask" in out

    def test_has_execute_method(self) -> None:
        out = _preview(["scheduler", "DailyReport"])
        assert "execute" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["scheduler", "DailyReport"], Path(tmp))
        assert len(files) == 1


# ── scaffold validator ─────────────────────────────────────────────────────────

class TestScaffoldValidator:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["validator", "ExamCode"])
        assert out

    def test_generates_validate_function(self) -> None:
        out = _preview(["validator", "ExamCode"])
        assert "validate_exam_code" in out

    def test_has_raises_value_error(self) -> None:
        out = _preview(["validator", "ExamCode"])
        assert "ValueError" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["validator", "ExamCode"], Path(tmp))
        assert len(files) == 1


# ── scaffold policy ────────────────────────────────────────────────────────────

class TestScaffoldPolicy:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["policy", "ExamAccess"])
        assert out

    def test_generates_policy_class(self) -> None:
        out = _preview(["policy", "ExamAccess"])
        assert "ExamAccessPolicy" in out

    def test_generates_result_class(self) -> None:
        out = _preview(["policy", "ExamAccess"])
        assert "ExamAccessPolicyResult" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["policy", "ExamAccess"], Path(tmp))
        assert len(files) == 1


# ── scaffold exception ─────────────────────────────────────────────────────────

class TestScaffoldException:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["exception", "Exam"])
        assert out

    def test_generates_base_error(self) -> None:
        out = _preview(["exception", "Exam"])
        assert "ExamError" in out

    def test_generates_not_found(self) -> None:
        out = _preview(["exception", "Exam"])
        assert "ExamNotFoundError" in out

    def test_generates_already_exists(self) -> None:
        out = _preview(["exception", "Exam"])
        assert "ExamAlreadyExistsError" in out

    def test_generates_access_denied(self) -> None:
        out = _preview(["exception", "Exam"])
        assert "ExamAccessDeniedError" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["exception", "Exam"], Path(tmp))
        assert len(files) == 1


# ── scaffold config ────────────────────────────────────────────────────────────

class TestScaffoldConfig:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["config", "Payment"])
        assert out

    def test_generates_settings_class(self) -> None:
        out = _preview(["config", "Payment"])
        assert "PaymentSettings" in out

    def test_has_env_prefix(self) -> None:
        out = _preview(["config", "Payment"])
        assert "PAYMENT_" in out

    def test_has_base_settings(self) -> None:
        out = _preview(["config", "Payment"])
        assert "BaseSettings" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["config", "Payment"], Path(tmp))
        assert len(files) == 1


# ── scaffold test ──────────────────────────────────────────────────────────────

class TestScaffoldTest:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["test", "UserService"])
        assert out

    def test_generates_test_class(self) -> None:
        out = _preview(["test", "UserService"])
        assert "TestUserService" in out

    def test_has_fixture(self) -> None:
        out = _preview(["test", "UserService"])
        assert "fixture" in out

    def test_has_async_test(self) -> None:
        out = _preview(["test", "UserService"])
        assert "asyncio" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["test", "UserService"], Path(tmp))
        assert len(files) == 1


# ── scaffold migration ─────────────────────────────────────────────────────────

class TestScaffoldMigration:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["migration", "add-users-table"])
        assert out

    def test_generates_upgrade(self) -> None:
        out = _preview(["migration", "add-users-table"])
        assert "upgrade" in out

    def test_generates_downgrade(self) -> None:
        out = _preview(["migration", "add-users-table"])
        assert "downgrade" in out

    def test_has_revision(self) -> None:
        out = _preview(["migration", "add-users-table"])
        assert "revision" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["migration", "add-users-table"], Path(tmp))
        assert len(files) == 1


# ── scaffold api ───────────────────────────────────────────────────────────────

class TestScaffoldApi:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["api", "users"])
        assert out

    def test_generates_router(self) -> None:
        out = _preview(["api", "users"])
        assert "APIRouter" in out or "router" in out

    def test_generates_crud_endpoints(self) -> None:
        out = _preview(["api", "users"])
        assert "list_users" in out
        assert "create_users" in out
        assert "get_users" in out
        assert "delete_users" in out

    def test_generates_request_body(self) -> None:
        out = _preview(["api", "users"])
        assert "UsersIn" in out

    def test_generates_response_schema(self) -> None:
        out = _preview(["api", "users"])
        assert "UsersOut" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["api", "users"], Path(tmp))
        assert len(files) == 1


# ── scaffold plugin (updated) ──────────────────────────────────────────────────

class TestScaffoldPlugin:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["plugin", "my-plugin"])
        assert out

    def test_generates_class_name(self) -> None:
        out = _preview(["plugin", "my-plugin"])
        assert "MyPluginPlugin" in out

    def test_shows_toml_comment(self) -> None:
        out = _preview(["plugin", "my-plugin"])
        assert "examverse.plugins" in out

    def test_shows_register_services(self) -> None:
        out = _preview(["plugin", "my-plugin"])
        assert "register_services" in out

    def test_hyphen_to_caps(self) -> None:
        out = _preview(["plugin", "hello-world"])
        assert "HelloWorldPlugin" in out

    def test_write_creates_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["plugin", "my-plugin"], Path(tmp))
        assert len(files) >= 1


# ── scaffold service ───────────────────────────────────────────────────────────

class TestScaffoldService:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["service", "payment-service"])
        assert out

    def test_generates_interface(self) -> None:
        out = _preview(["service", "payment-service"])
        assert "IPaymentService" in out

    def test_generates_implementation(self) -> None:
        out = _preview(["service", "payment-service"])
        assert "PaymentService" in out

    def test_shows_abstract_method(self) -> None:
        out = _preview(["service", "payment-service"])
        assert "abstractmethod" in out or "ABC" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["service", "payment-service"], Path(tmp))
        assert len(files) == 1


# ── scaffold repository ────────────────────────────────────────────────────────

class TestScaffoldRepository:
    def test_preview_exits_zero(self) -> None:
        out = _preview(["repository", "user"])
        assert out

    def test_generates_interface(self) -> None:
        out = _preview(["repository", "user"])
        assert "IUserRepository" in out

    def test_generates_in_memory_impl(self) -> None:
        out = _preview(["repository", "user"])
        assert "InMemoryUserRepository" in out

    def test_shows_crud_methods(self) -> None:
        out = _preview(["repository", "user"])
        assert "get" in out and "save" in out and "delete" in out

    def test_write_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            files = _write(["repository", "user"], Path(tmp))
        assert len(files) == 1
