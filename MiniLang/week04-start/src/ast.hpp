/*
 * Educational Mini compiler.
 * Demonstrates the translation pipeline for documented Mini 1.0 programs.
 * Diagnostics and edge-case handling are intentionally limited.
 * See the project specification and documented limitations.
 */

#pragma once

#include "source.hpp"

#include <cstddef>
#include <memory>
#include <optional>
#include <string>
#include <variant>
#include <vector>

namespace mini {

using SymbolId = std::size_t;

struct NumberExpression {
  double value;
};

struct StringExpression {
  std::string value;
};

struct BoolExpression {
  bool value;
};

struct NilExpression {};

struct VariableExpression {
  std::string name;
  std::optional<SymbolId> resolved_id;
};

struct Expression;
using ExpressionPtr = std::unique_ptr<Expression>;

struct GroupingExpression {
  ExpressionPtr expression;
};

struct Expression {
  SourceSpan span;
  std::variant<NumberExpression, StringExpression, BoolExpression,
               NilExpression, VariableExpression, GroupingExpression>
      node;
};

struct PrintStatement {
  Expression expression;
};

struct VarStatement {
  std::string name;
  SourceSpan name_span;
  Expression initializer;
  std::optional<SymbolId> resolved_id;
};

struct AssignmentStatement {
  std::string name;
  SourceSpan name_span;
  Expression value;
  std::optional<SymbolId> resolved_id;
};

struct ExpressionStatement {
  Expression expression;
};

struct Statement;

struct BlockStatement {
  std::vector<Statement> statements;
};

struct Statement {
  SourceSpan span;
  std::variant<PrintStatement, VarStatement, AssignmentStatement,
               ExpressionStatement, BlockStatement>
      node;
};

struct Program {
  std::vector<Statement> main_body;
};

std::string formatAst(const Program &program);

} // namespace mini
