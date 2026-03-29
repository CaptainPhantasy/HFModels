#!/usr/bin/env python3
"""
Multi-language code examples generator.
Produces real executable code in Go, Rust, Java, Bash.
"""
import json


SYSTEM_PROMPTS = [
    "You are an elite coding assistant. Write production-quality code with proper error handling.",
    "You are a systems programmer. Write performant, idiomatic code for the target language.",
    "You are a backend engineer. Design scalable, maintainable code patterns.",
    "You are a DevOps engineer. Write robust shell scripts and automation.",
    "You are a database expert. Write optimized, secure SQL queries.",
]


def go_examples():
    """Generate Go code examples."""
    examples = []

    # 1. Goroutine pool
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Implement a goroutine pool in Go that limits concurrent workers to N.",
        "assistant": '''package main

import (
    "context"
    "sync"
)

type Job func() error

type Pool struct {
    jobs    chan Job
    wg      sync.WaitGroup
    ctx     context.Context
    cancel  context.CancelFunc
}

func NewPool(workers int) *Pool {
    ctx, cancel := context.WithCancel(context.Background())
    p := &Pool{
        jobs:   make(chan Job, workers*2),
        ctx:    ctx,
        cancel: cancel,
    }
    for i := 0; i < workers; i++ {
        p.wg.Add(1)
        go p.worker()
    }
    return p
}

func (p *Pool) worker() {
    defer p.wg.Done()
    for {
        select {
        case job, ok := <-p.jobs:
            if !ok {
                return
            }
            job()
        case <-p.ctx.Done():
            return
        }
    }
}

func (p *Pool) Submit(job Job) {
    select {
    case p.jobs <- job:
    case <-p.ctx.Done():
    }
}

func (p *Pool) Wait() {
    close(p.jobs)
    p.wg.Wait()
}

func (p *Pool) Close() {
    p.cancel()
}'''
    })

    # 2. Error wrapping
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Write a Go function that wraps errors with stack traces and context.",
        "assistant": '''package errors

import (
    "fmt"
    "runtime"
)

type StackError struct {
    msg   string
    cause error
    stack []string
}

func (e *StackError) Error() string {
    return fmt.Sprintf("%s: %v\\n%s", e.msg, e.cause, e.stackTrace())
}

func (e *StackError) Unwrap() error {
    return e.cause
}

func (e *StackError) stackTrace() string {
    var lines []string
    for _, pc := range e.stack[:len(e.stack)-1] {
        fn := runtime.FuncForPC(pc)
        file, line := fn.FileLine(pc)
        lines = append(lines, fmt.Sprintf("  %s:%d %s", file, line, fn.Name()))
    }
    return joinLines(lines)
}

func Wrap(err error, msg string) error {
    if err == nil {
        return nil
    }
    return &StackError{
        msg:   msg,
        cause: err,
        stack: make([]uintptr, 32),
    }
}

func getStack() []uintptr {
    n := runtime.Callers(3, make([]uintptr, 32))
    return pcs[:n]
}'''
    })

    # 3. Context timeout
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Implement a function with context timeout and graceful shutdown.",
        "assistant": '''package main

import (
    "context"
    "fmt"
    "net/http"
    "time"
)

type Server struct {
    http   *http.Server
    done   chan struct{}
}

func NewServer(addr string, handler http.Handler) *Server {
    return &Server{
        http: &http.Server{
            Addr:    addr,
            Handler: handler,
        },
        done: make(chan struct{}),
    }
}

func (s *Server) Start() error {
    go s.run()
    return s.http.ListenAndServe()
}

func (s *Server) run() {
    defer close(s.done)
    if err := s.http.ListenAndServe(); err != http.ErrServerClosed {
        fmt.Printf("server error: %v", err)
    }
}

func (s *Server) Stop(timeout time.Duration) error {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()
    return s.http.Shutdown(ctx)
}'''
    })

    # 4. Slice tricks
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Show idiomatic Go slice operations: filter, map, reduce.",
        "assistant": '''package slices

func Filter[T any](s []T, pred func(T) bool) []T {
    result := make([]T, 0, len(s))
    for _, v := range s {
        if pred(v) {
            result = append(result, v)
        }
    }
    return result
}

func Map[T, U any](s []T, fn func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = fn(v)
    }
    return result
}

func Reduce[T, U any](s []T, init U, fn func(U, T) U) U {
    acc := init
    for _, v := range s {
        acc = fn(acc, v)
    }
    return acc
}

func FlatMap[T, U any](s []T, fn func(T) []U) []U {
    var result []U
    for _, v := range s {
        result = append(result, fn(v)...)
    }
    return result
}'''
    })

    # 5. Once pattern
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Implement sync.Once for lazy initialization with thread safety.",
        "assistant": '''package sync

import (
    "sync/atomic"
)

type Once struct {
    done uint32
    m    Mutex
}

func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 {
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}'''
    })

    return examples


def rust_examples():
    """Generate Rust code examples."""
    examples = []

    # 1. Result chaining
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Write idiomatic Rust error handling with Result chaining.",
        "assistant": '''use std::fs;
use std::io;
use std::path::Path;

#[derive(Debug)]
enum Error {
    Io(io::Error),
    Parse(json::Error),
    NotFound(String),
}

impl From<io::Error> for Error {
    fn from(e: io::Error) -> Self {
        Error::Io(e)
    }
}

impl From<json::Error> for Error {
    fn from(e: json::Error) -> Self {
        Error::Parse(e)
    }
}

fn read_config(path: &Path) -> Result<Config, Error> {
    let contents = fs::read_to_string(path)?;
    let json: serde_json::Value = contents.parse()?;
    Config::from_json(&json)
}

fn main() -> Result<(), Error> {
    let config = read_config(Path::new("config.json"))?;
    println!("Loaded: {:?}", config);
    Ok(())
}'''
    })

    # 2. Iterator chains
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Show advanced Rust iterator patterns with collect, fold, and custom iterators.",
        "assistant": '''use std::collections::HashMap;

struct WordCounter {
    text: String,
}

impl WordCounter {
    fn new(text: String) -> Self {
        Self { text }
    }

    fn count_words(&self) -> HashMap<&str, usize> {
        self.text
            .split_whitespace()
            .fold(HashMap::new(), |mut acc, word| {
                *acc.entry(word).or_insert(0) += 1;
                acc
            })
    }

    fn top_n(&self, n: usize) -> Vec<(&str, usize)> {
        let mut counts: Vec<_> = self.count_words().into_iter().collect();
        counts.sort_by(|a, b| b.1.cmp(&a.1));
        counts.into_iter().take(n).collect()
    }
}

struct Fibonacci {
    current: u64,
    next: u64,
}

impl Default for Fibonacci {
    fn default() -> Self {
        Self { current: 0, next: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let current = self.current;
        self.current = self.next;
        self.next += current;
        Some(current)
    }
}'''
    })

    # 3. Trait objects
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Implement the Strategy pattern with trait objects in Rust.",
        "assistant": '''trait SortStrategy<T> {
    fn sort(&self, data: &mut [T])
    where
        T: Ord;
}

struct BubbleSort;

impl<T: Ord> SortStrategy<T> for BubbleSort {
    fn sort(&self, data: &mut [T]) {
        let len = data.len();
        for i in 0..len {
            for j in 0..len - i - 1 {
                if data[j] > data[j + 1] {
                    data.swap(j, j + 1);
                }
            }
        }
    }
}

struct QuickSort;

impl<T: Ord> SortStrategy<T> for QuickSort {
    fn sort(&self, data: &mut [T]) {
        if data.len() <= 1 {
            return;
        }
        let pivot = data.len() / 2;
        data.swap(pivot, data.len() - 1);
        let mut i = 0;
        for j in 0..data.len() - 1 {
            if data[j] <= data[data.len() - 1] {
                data.swap(i, j);
                i += 1;
            }
        }
        data.swap(i, data.len() - 1);
        let (lo, hi) = data.split_at_mut(i);
        self.sort(lo);
        self.sort(hi);
    }
}

struct Sorter<T> {
    strategy: Box<dyn SortStrategy<T>>,
}

impl<T> Sorter<T> {
    fn new(strategy: Box<dyn SortStrategy<T>>) -> Self {
        Self { strategy }
    }

    fn sort(&self, data: &mut [T])
    where
        T: Ord,
    {
        self.strategy.sort(data);
    }
}'''
    })

    # 4. Lifetimes
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Explain and implement Rust lifetime annotations in structs and functions.",
        "assistant": '''// Lifetime annotations describe the relationships between references
// The compiler uses them to ensure all references are valid

// In structs
struct Parser<'a> {
    input: &'a str,
    position: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self {
        Parser { input, position: 0 }
    }

    fn current_slice(&self) -> &'a str {
        &self.input[self.position..]
    }
}

// Lifetime elision rules (compiler infers these):
// 1. Each elided lifetime in input becomes a distinct lifetime param
// 2. If there's exactly one input lifetime, assign it to all output lifetimes
// 3. If there's a &self or &mut self, self's lifetime is assigned to all outputs

// Example where explicit lifetimes are needed:
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}'''
    })

    # 5. Async/Await
    examples.append({
        "system": SYSTEM_PROMPTS[1],
        "user": "Write async Rust code with tokio for concurrent operations.",
        "assistant": '''use tokio::sync::mpsc;
use tokio::time::{sleep, Duration};

async fn process_batch(items: Vec<i32>) -> Vec<i32> {
    let mut results = Vec::with_capacity(items.len());
    for item in items {
        results.push(process_item(item).await);
    }
    results
}

async fn process_item(n: i32) -> i32 {
    sleep(Duration::from_millis(10)).await;
    n * 2
}

async fn run_with_timeout<F, T>(fut: F, timeout: Duration) -> Option<T>
where
    F: Future<Output = T>,
{
    tokio::time::timeout(timeout, fut).await.ok()
}

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel::<i32>(100);
    
    tokio::spawn(async move {
        for i in 0..10 {
            tx.send(i).await.unwrap();
        }
    });
    
    let results: Vec<i32> = while let Some(v) = rx.recv().await {
        v * 2
    }.collect();
    
    println!("Results: {:?}", results);
}'''
    })

    return examples


def java_examples():
    """Generate Java code examples."""
    examples = []

    # 1. Stream API
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Write Java code demonstrating advanced Stream API operations.",
        "assistant": '''import java.util.*;
import java.util.stream.*;

public class StreamExamples {
    
    public static void main(String[] args) {
        List<Order> orders = getOrders();
        
        // Group by status
        Map<OrderStatus, List<Order>> byStatus = orders.stream()
            .collect(Collectors.groupingBy(Order::getStatus));
        
        // Partition by amount
        Map<Boolean, List<Order>> byHighValue = orders.stream()
            .collect(Collectors.partitioningBy(
                o -> o.getTotal().compareTo(BigDecimal.valueOf(1000)) > 0
            ));
        
        // Multi-level grouping
        Map<String, Map<OrderStatus, List<Order>>> byCustomerAndStatus = orders.stream()
            .collect(Collectors.groupingBy(
                Order::getCustomerId,
                LinkedHashMap::new,
                Collectors.groupingBy(Order::getStatus)
            ));
        
        // Custom collector
        String report = orders.stream()
            .collect(Collectors.collectingAndThen(
                Collectors.toList(),
                list -> generateReport(list)
            ));
    }
    
    private static String generateReport(List<Order> orders) {
        return orders.stream()
            .map(Object::toString)
            .collect(Collectors.joining("\\n"));
    }
}'''
    })

    # 2. CompletableFuture
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Implement async operations with CompletableFuture in Java.",
        "assistant": '''import java.util.concurrent.*;
import java.util.List;

public class AsyncService {
    private final ExecutorService executor = Executors.newFixedThreadPool(10);
    
    public CompletableFuture<Result> processAsync(Data data) {
        return CompletableFuture
            .supplyAsync(() -> validate(data), executor)
            .thenApply(this::transform)
            .thenCompose(this::persist)
            .exceptionally(ex -> {
                logger.error("Processing failed", ex);
                return Result.failure(ex.getMessage());
            });
    }
    
    public CompletableFuture<List<Result>> processBatch(List<Data> items) {
        List<CompletableFuture<Result>> futures = items.stream()
            .map(this::processAsync)
            .toList();
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .toList());
    }
    
    private Data validate(Data data) {
        if (data == null) throw new IllegalArgumentException();
        return data;
    }
    
    private TransformedData transform(Data data) {
        return new TransformedData(data.getValue() * 2);
    }
    
    private CompletableFuture<Result> persist(TransformedData data) {
        return CompletableFuture.supplyAsync(() -> db.save(data), executor);
    }
}'''
    })

    # 3. Builder pattern
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Implement the Builder pattern with method chaining in Java.",
        "assistant": '''public class User {
    private final String id;
    private final String name;
    private final String email;
    private final int age;
    private final List<String> roles;
    private final Map<String, Object> metadata;
    
    private User(Builder builder) {
        this.id = builder.id;
        this.name = builder.name;
        this.email = builder.email;
        this.age = builder.age;
        this.roles = Collections.unmodifiableList(builder.roles);
        this.metadata = Collections.unmodifiableMap(builder.metadata);
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static class Builder {
        private String id;
        private String name;
        private String email;
        private int age;
        private List<String> roles = new ArrayList<>();
        private Map<String, Object> metadata = new HashMap<>();
        
        public Builder id(String id) {
            this.id = id;
            return this;
        }
        
        public Builder name(String name) {
            this.name = name;
            return this;
        }
        
        public Builder email(String email) {
            this.email = email;
            return this;
        }
        
        public Builder age(int age) {
            this.age = age;
            return this;
        }
        
        public Builder addRole(String role) {
            this.roles.add(role);
            return this;
        }
        
        public Builder metadata(String key, Object value) {
            this.metadata.put(key, value);
            return this;
        }
        
        public User build() {
            return new User(this);
        }
    }
}

// Usage:
User user = User.builder()
    .id("123")
    .name("John")
    .email("john@example.com")
    .age(30)
    .addRole("admin")
    .addRole("user")
    .metadata("department", "engineering")
    .build();'''
    })

    # 4. Optional chaining
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Demonstrate Java Optional patterns for null-safe operations.",
        "assistant": '''import java.util.Optional;
import java.util.stream.Stream;

public class OptionalPatterns {
    
    // Safe navigation with orElse
    public String getDefaultName(User user) {
        return Optional.ofNullable(user)
            .map(User::getName)
            .orElse("Anonymous");
    }
    
    // Conditional processing
    public Optional<String> getEmailIfAdmin(User user) {
        return Optional.ofNullable(user)
            .filter(User::isAdmin)
            .map(User::getEmail);
    }
    
    // Chained transformations
    public Optional<Integer> parseAndDouble(String input) {
        return Optional.ofNullable(input)
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .map(Integer::parseInt)
            .map(n -> n * 2);
    }
    
    // Stream from Optional
    public Stream<String> getRolesStream(User user) {
        return Optional.ofNullable(user)
            .map(User::getRoles)
            .map(List::stream)
            .orElse(Stream.empty());
    }
    
    // Optional in collections
    public Map<String, User> filterPresent(List<Optional<User>> optionals) {
        return optionals.stream()
            .flatMap(Optional::stream)
            .collect(Collectors.toMap(User::getId, u -> u));
    }
}'''
    })

    # 5. Records (Java 17+)
    examples.append({
        "system": SYSTEM_PROMPTS[2],
        "user": "Show Java record patterns for immutable data classes.",
        "assistant": '''// Records are immutable data carriers with auto-generated methods

public record Point(double x, double y) {
    // Compact canonical constructor for validation
    public Point {
        if (x < 0 || y < 0) {
            throw new IllegalArgumentException("Coordinates must be positive");
        }
    }
    
    // Additional methods
    public double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }
    
    // Static factory
    public static Point origin() {
        return new Point(0, 0);
    }
}

// Sealed interfaces with records
public sealed interface Shape permits Circle, Rectangle, Triangle {
    double area();
}

public record Circle(double radius) implements Shape {
    public Circle {
        if (radius < 0) throw new IllegalArgumentException();
    }
    @Override
    public double area() { return Math.PI * radius * radius; }
}

public record Rectangle(double width, double height) implements Shape {
    @Override
    public double area() { return width * height; }
}

public record Triangle(double base, double height) implements Shape {
    @Override
    public double area() { return base * height / 2; }
}'''
    })

    return examples


def bash_examples():
    """Generate Bash script examples."""
    examples = []

    # 1. Error handling
    examples.append({
        "system": SYSTEM_PROMPTS[3],
        "user": "Write a bash script with proper error handling and logging.",
        "assistant": '''#!/usr/bin/env bash
set -euo pipefail
IFS=$'\\n\\t'

# Logging
readonly LOG_FILE="/var/log/$(basename "$0").log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
log_error() { log "ERROR: $*" >&2; }
log_info() { log "INFO: $*"; }

# Exit handlers
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code $exit_code"
    fi
    # Cleanup temporary files
    rm -rf "$TEMP_DIR" 2>/dev/null || true
    exit $exit_code
}
trap cleanup EXIT ERR

# Validate dependencies
check_deps() {
    local deps=("jq" "curl" "git")
    for dep in "${deps[@]}"; do
        command -v "$dep" >/dev/null || {
            log_error "Missing dependency: $dep"
            exit 1
        }
    done
}

# Main
main() {
    check_deps
    TEMP_DIR=$(mktemp -d)
    log_info "Starting process..."
    # Your logic here
}

main "$@"'''
    })

    # 2. Parallel processing
    examples.append({
        "system": SYSTEM_PROMPTS[3],
        "user": "Write a bash script that processes files in parallel with xargs.",
        "assistant": '''#!/usr/bin/env bash
set -euo pipefail

# Configuration
readonly MAX_JOBS=4
readonly INPUT_DIR="./input"
readonly OUTPUT_DIR="./output"

# Process single file
process_file() {
    local input="$1"
    local output="$2"
    local temp=$(mktemp)
    
    # Simulate work
    sleep 0.1
    
    # Example: transform JSON
    jq '.metadata.processed = true' "$input" > "$temp"
    mv "$temp" "$output"
    
    echo "Processed: $input"
}

export -f process_file
export OUTPUT_DIR

# Find all files and process in parallel
find "$INPUT_DIR" -type f -name "*.json" | \\
    xargs -P "$MAX_JOBS" -I {} bash -c \\
        'process_file "$1" "$OUTPUT_DIR/$(basename "$1")"' _ {}

echo "Done. Processed $(find "$OUTPUT_DIR" -type f | wc -l) files."'''
    })

    # 3. JSON parsing
    examples.append({
        "system": SYSTEM_PROMPTS[3],
        "user": "Write bash functions to parse and manipulate JSON with jq.",
        "assistant": '''#!/usr/bin/env bash

# jq wrapper functions for common operations
readonly JQ_BIN="jq"

# Get value at path
jq_get() {
    local json="$1"
    local path="$2"
    echo "$json" | "$JQ_BIN" -r "$path"
}

# Set value at path
jq_set() {
    local json="$1"
    local path="$2"
    local value="$3"
    echo "$json" | "$JQ_BIN" "$path = $value"
}

# Map array
jq_map() {
    local json="$1"
    local transform="$2"
    echo "$json" | "$JQ_BIN" "[.[] | $transform]"
}

# Filter array
jq_filter() {
    local json="$1"
    local predicate="$2"
    echo "$json" | "$JQ_BIN" "[.[] | select($predicate)]"
}

# Merge objects
jq_merge() {
    local json1="$1"
    local json2="$2"
    echo "$json1" | "$JQ_BIN" -s '.[0] * .[1]' <<< "$json2"
}

# Usage example
config='{"app": {"port": 8080, "host": "localhost"}}'
port=$(jq_get "$config" '.app.port')
echo "Port: $port"'''
    })

    # Example usage in script
    examples.append({
        "system": SYSTEM_PROMPTS[3],
        "user": "Write a bash script that fetches JSON from an API and processes it.",
        "assistant": '''#!/usr/bin/env bash
set -euo pipefail

API_BASE="https://api.github.com"

fetch_repos() {
    local user="$1"
    curl -s "${API_BASE}/users/${user}/repos" | \\
        jq -r '.[] | select(.fork == false) | .name'
}

get_stats() {
    local repo="$1"
    curl -s "${API_BASE}/repos/${user}/${repo}" | \\
        jq '{stars: .stargazers_count, forks: .forks_count, issues: .open_issues_count}'
}

main() {
    local user="${1:-torvalds}"
    echo "Fetching repos for: $user"
    
    while IFS= read -r repo; do
        stats=$(get_stats "$repo")
        stars=$(echo "$stats" | jq -r '.stars')
        echo "$repo: $stars stars"
    done < <(fetch_repos "$user" | head -10)
}

main "$@"'''
    })

    return examples


def generate_multi_lang(output_path):
    """Generate all multi-language examples and write to JSONL."""
    all_examples = []
    
    all_examples.extend(go_examples())
    all_examples.extend(rust_examples())
    all_examples.extend(java_examples())
    all_examples.extend(bash_examples())
    
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            record = {
                "messages": [
                    {"role": "system", "content": ex["system"]},
                    {"role": "user", "content": ex["user"]},
                    {"role": "assistant", "content": ex["assistant"]}
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    
    return count


if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "multi_lang_training.jsonl"
    count = generate_multi_lang(output)
    print(f"Generated {count} multi-language examples")
