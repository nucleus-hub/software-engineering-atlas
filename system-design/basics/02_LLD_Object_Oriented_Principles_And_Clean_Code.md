# LLD: Object-Oriented Principles & Clean Code

## Terms to know before you start

You do not need to memorize these. Come back to this table whenever a term feels unfamiliar.

| Term | What it means in plain words |
|---|---|
| **Class and object** | A class is a blueprint that describes data and the methods that work on it. An object is one concrete instance created from that blueprint. |
| **Interface** | A list of methods that a class promises to provide, without saying how. Code that uses an interface works with any class that implements it. |
| **Implementation** | A class that provides the actual code behind an interface. One interface can have many implementations. |
| **Caller (or client)** | The code that uses an object by calling its methods. |
| **Invariant** | A rule about an object's data that must always be true, such as "a cart's total always equals the sum of its line items minus its discounts". |
| **Contract** | Everything a caller may rely on when using an object: its methods, what they accept, what they return, and how they fail. |
| **Dependency** | Something a class needs in order to do its job. If class A calls class B, then A depends on B. |
| **Wiring** | The code that creates objects and connects them to their dependencies, usually at application startup. |
| **Coupling** | How much one class knows about another. High coupling means a change in one class forces changes in others. |
| **Cohesion** | How closely the code inside one class belongs together. High cohesion means everything in the class serves one purpose. |
| **Refactoring** | Changing the structure of code without changing what it does, usually to make the next change easier. |
| **Test double (fake)** | A simple stand-in object used in tests instead of a real dependency, such as an in-memory cart store that keeps carts in a map instead of a real database. |

??? info "Java syntax used on this page (open if you learned Java before version 17)"
    - **`final class`** means the class cannot be extended by inheritance.
    - **`record`** is a short way to declare a class whose job is to hold data. `record Point(int x, int y) {}` automatically creates private final fields, a constructor, and the accessor methods `x()` and `y()`.
    - **`switch` with `->`** is the newer switch syntax. Each case runs only its own branch, so there is no `break` and no accidental fall-through.
    - **`List.of(...)`** and **`Map.of(...)`** create small collections that cannot be modified afterwards. **`List.copyOf(list)`** makes an unmodifiable copy of an existing list.
    - **`Optional<T>`** holds either one value or nothing. A method that returns `Optional.empty()` is saying "nothing was found", and the caller is forced to handle that case instead of receiving `null`.

---

## 1. The running example: one messy class

Every principle on this page is easier to understand when you watch it fix a real problem. So instead of using a different example for each idea, the whole page improves one piece of code step by step.

In **Basics 1**, you sized a cart-and-checkout flow and drew its main boxes: a cart service, a cache, a checkout service, a durable order store, and a payment gateway. This page zooms into the code inside the checkout box. Since launch, the product team has also added three discount features: percentage-off codes, free-shipping promotions, and buy-one-get-one deals. Here is a first version of the checkout code that works, but that is painful to change:

```java
class CheckoutManager {
    public String cartId;                      // the cart API fills these in, and anyone can set them to anything
    public double total;
    public String discountType;                // "NONE", "PERCENTAGE", "FREE_SHIPPING", or "BOGO"

    String checkout(String cartId, String discountCode, String cardToken) {
        String cached = redis.get("cart:" + cartId);                                            // cache plumbing
        Row row = (cached != null) ? Row.fromJson(cached)
                : new PostgresClient(DB_URL).query("SELECT * FROM carts WHERE id = ?", cartId);   // SQL plumbing
        if (cached == null) redis.set("cart:" + cartId, row.toJson());

        double total = row.subtotal();
        switch (row.discountType()) {                                                           // discount rules
            case "PERCENTAGE"    -> total = total * (1 - row.discountValue());
            case "FREE_SHIPPING" -> total = total - row.shippingCost();
            case "BOGO"          -> total = total - row.cheapestItemPrice();
        }
        String receipt = new StripeClient(STRIPE_KEY).charge(cardToken, total);                 // payment plumbing
        emailer.send(row.customerEmail(), "Your receipt", receipt);                             // notification plumbing
        return receipt;
    }
}
```

This class has five separate problems, and each level below fixes one of them:

| Problem in `CheckoutManager` | Fixed in |
|---|---|
| Any caller can set `total` or `discountType` directly, including a negative total or a made-up discount. | Level 1: Encapsulation |
| The checkout logic is buried under cache, SQL, and payment plumbing, and a missing cart is never handled. | Level 2: Abstraction |
| Every new discount type means editing the `switch`, and every other `switch` on discount type. | Level 3: Polymorphism |
| A cart can only have one discount, so "10% off **and** free shipping" cannot exist. | Level 4: Composition over inheritance |
| The class knows about Redis, Postgres, Stripe, and email all at once. | Level 5: Coupling and cohesion |

---

## 2. The four pillars of object-oriented design

![Object design flow from encapsulation to local evolution](assets/topic-02/oop_mental_model.png)

The four pillars build on each other. Encapsulation protects data, abstraction hides details behind a simple interface, polymorphism lets many implementations share one interface, and composition assembles small objects into bigger behavior. Together they lead to the goal shown at the bottom of the diagram: when requirements change, only a small number of classes need to change.

### Level 1: Encapsulation, keeping the rules with the data

**Encapsulation** means an object keeps its data private and only exposes methods that keep that data valid. The rules about the data (its invariants) are enforced in exactly one place: inside the object that owns the data.

In `CheckoutManager`, the fields are public, so nothing stops a caller from setting `total = -50` or `discountType = "FREE_EVERYTHING"`, a value nothing on this page ever defined. Every caller would have to remember to validate the data, and sooner or later one of them would forget.

The fix is to make each object responsible for its own validity. It checks its data once, in the constructor, and never allows that data to change afterwards:

```java
record Money(long cents, String currency) {
    Money {                                            // runs before the field is set
        if (cents < 0) throw new IllegalArgumentException("a price cannot be negative");
        if (currency == null || currency.length() != 3)
            throw new IllegalArgumentException("currency must be a 3-letter code, such as MXN");
    }
    Money plus(Money other) {                          // pesos plus rand is a bug, not a sum
        if (!currency.equals(other.currency))
            throw new IllegalArgumentException("cannot add " + other.currency + " to " + currency);
        return new Money(cents + other.cents, currency);
    }
}

record CartItem(String productId, int quantity, Money unitPrice) {
    CartItem {
        if (quantity <= 0) throw new IllegalArgumentException("quantity must be at least 1");
        if (productId == null || unitPrice == null) throw new IllegalArgumentException("productId and unitPrice are required");
    }
}
```

Now an invalid price or quantity simply cannot exist. Any method that receives a `Money` or a `CartItem` can trust it without checking it again. Wrapping an amount in its own `Money` type follows the same idea: a method that receives a `Money` never needs to re-check for negative amounts or missing currencies, and nobody can accidentally pass a raw `double` where a validated price was expected — which matters a great deal once that number is about to be charged to a real credit card. And because the same code runs in Mexico, Canada, Chile, and South Africa, `plus` refusing to mix currencies turns a silent pricing bug into a loud one.

!!! warning "A common trap"
    Making every field private and then adding a public setter for each one is not encapsulation. Callers can still put the object into any state they like, so the rules still live in the callers. Only add methods that keep the object valid.

!!! question "Practice"
    What is wrong with this class, and how would you fix it?

    ```java
    class Invoice {
        public List<LineItem> lines = new ArrayList<>();
        public double total;
    }
    // A caller elsewhere:
    invoice.lines.add(line);
    invoice.total += line.amount();
    ```

??? success "Answer"
    The rule "the total always equals the sum of the line amounts" lives in the callers. If any caller adds a line and forgets to update the total, the invoice becomes wrong, and nothing detects it. The fix is to make the fields private and give the invoice an `addLine(LineItem line)` method that updates both together, or, even simpler, to compute `total()` from the lines whenever it is asked for.

### Level 2: Abstraction, hiding the how

**Abstraction** means callers depend on *what* an object does, not *how* it does it. The caller states its intent, and the details stay hidden behind a simple interface.

In `CheckoutManager`, the checkout method checks Redis, falls back to a SQL query, and then fills the cache, all before it can do its actual job. The code that decides how much to charge a shopper should not need to know how carts are stored. We hide storage behind an interface:

```java
interface CartRepository {
    Optional<Cart> findById(CartId id);
    void save(Cart cart);
}

final class PostgresCartRepository implements CartRepository {
    public Optional<Cart> findById(CartId id) {
        // the SQL query, and the mapping from table rows to Cart objects, live here and only here
    }
    public void save(Cart cart) { ... }
}
```

Notice that `findById` returns an `Optional` rather than a cart that might be `null`. A good abstraction hides details the caller does not need, but it must not hide information the caller needs in order to make a decision. A missing cart is normal, because a session can expire or a cart ID can be mistyped, and the caller must decide to show a "your cart could not be found" page. So "nothing was found" is part of the contract. The messy version simply forgot about this case.

What about the cache? It has disappeared from the business logic as well. **Basics 3** shows how to put it back behind this same interface without editing `PostgresCartRepository` at all.

!!! question "Practice"
    A caller exports a report by opening a file, writing a header row, writing every data row, flushing the stream, and closing the file. What would a better abstraction look like?

??? success "Answer"
    Hide the steps behind an intent-based method such as `reportExporter.export(report, destination)`. The caller only expresses what it wants, and the file-handling steps live inside one exporter class. If the format later changes from CSV to Excel, only the exporter changes, and none of its callers do.

### Level 3: Polymorphism, replacing the type switch

**Polymorphism** means the same method call can behave differently depending on which object receives it. It lets you replace `if` and `switch` statements that check an object's type with a single call through an interface.

In `CheckoutManager`, every new discount means editing the `switch`. Worse, in real code the same `switch` on discount type tends to appear in several places, such as checkout, the cart preview page, and the admin tool that explains a refund, and every one of them must be found and updated.

Instead, each discount type becomes its own class behind one interface:

```java
interface DiscountRule {
    Money apply(Money subtotal);
}

final class PercentageOffRule implements DiscountRule {
    private final double fraction;                 // e.g. 0.10 for 10% off
    PercentageOffRule(double fraction) { this.fraction = fraction; }

    public Money apply(Money subtotal) {
        return subtotal.minus(subtotal.times(fraction));
    }
}
// FreeShippingRule and BogoRule follow exactly the same shape.
```

The `switch` disappears, and one call, `rule.apply(subtotal)`, works for every rule, including rules added later. When marketing asks for a "spend MX$1,000, get MX$150 off" rule, that becomes a new class, and none of the existing, already-tested rules are edited.

!!! tip "A switch is not always wrong"
    Polymorphism is the right tool when new types keep arriving and each type has its own behavior. A plain `switch` is perfectly fine for a small, fixed set of values that rarely changes, such as the days of the week. Choose based on what is likely to change.

??? info "Go deeper (optional): sealed types and exhaustive switches"
    Modern Java offers a middle ground. A `sealed` interface lists every allowed implementation, and a `switch` over it must handle every one of them, or the code does not compile:

    ```java
    sealed interface Shape permits Circle, Square {}
    record Circle(double radius) implements Shape {}
    record Square(double side) implements Shape {}

    double area(Shape shape) {
        return switch (shape) {                        // no default branch is needed
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Square s -> s.side() * s.side();
        };
    }
    ```

    The trade-off is known as the *expression problem*. Polymorphism makes adding a new **type** cheap and a new **operation** expensive; a sealed switch is the reverse, and the compiler points out every switch that a new type must update.

!!! question "Practice"
    How would you remove the type checks from this method?

    ```java
    double area(Shape shape) {
        if (shape.type.equals("circle")) return Math.PI * shape.radius * shape.radius;
        if (shape.type.equals("square")) return shape.side * shape.side;
        throw new IllegalArgumentException("unknown shape");
    }
    ```

??? success "Answer"
    Make `Shape` an interface with an `area()` method, and let `Circle` and `Square` each implement it. The caller then simply calls `shape.area()`. A new shape, such as a triangle, becomes a new class, and the existing code does not change.

### Level 4: Composition over inheritance

**Inheritance** creates an *is-a* relationship: a subclass reuses its parent's code and promises to behave like its parent everywhere. **Composition** creates a *has-a* relationship: an object holds other objects and hands work over to them.

The classic illustration is a bird that can fly, and a penguin that cannot:

![Comparison of inheritance and composition for flight behavior](assets/topic-02/composition_vs_inheritance.png)

If `Penguin extends Bird` and overrides `fly()` to throw an exception, any code that calls `bird.fly()` on a list of birds crashes on the penguin. With composition, a bird *has* a flight behavior, and a penguin is simply a bird given `NoFlight`. No method is overridden, and nothing breaks.

The cart runs into a similar problem as soon as a customer asks to combine a percentage-off code *and* a free-shipping promotion. The old `discountType` field can hold only one value. Inheritance tempts us towards `PercentageCart extends Cart` and `FreeShippingCart extends Cart`, and then `PercentageFreeShippingCart`, `PercentageFreeShippingBogoCart`, and so on. Three discounts already allow seven combinations, and every new discount type doubles the count. Composition avoids that explosion: a cart *has* a list of rules, and the final price applies every rule in turn.

```java
record Cart(CartId id, List<CartItem> items, List<DiscountRule> rules) {
    Cart {
        // ...the same checks as in Level 1...
        rules = List.copyOf(rules);                    // a private copy that callers cannot modify later
    }

    Money total() {
        Money subtotal = items.stream().map(CartItem::lineTotal).reduce(Money.zero(), Money::plus);
        Money discounted = subtotal;
        for (DiscountRule rule : rules) discounted = rule.apply(discounted);   // every rule gets a turn
        return discounted;
    }
}

// A cart with a 10% off code and free shipping is simply a cart with two rules:
new Cart(cartId, items, List.of(new PercentageOffRule(0.10), new FreeShippingRule(shippingCost)));
```

A new discount is one new rule class, and it combines with every existing rule for free. `List.copyOf` is encapsulation at work again: without it, a caller could quietly add or remove rules after the cart was priced.

Inheritance is still the right tool when the relationship is a true *is-a*, the hierarchy is shallow (one or two levels), and every subclass keeps every promise its parent makes. A quick test: if you are about to override a method just to throw an exception or do nothing, the relationship was never *is-a*, so use composition instead.

??? info "Go deeper (optional): the fragile base class problem"
    Inheritance ties a subclass to its parent's *implementation*, not just its interface. This example, from the book *Effective Java*, tries to count how many items are added to a set:

    ```java
    class InstrumentedHashSet<E> extends HashSet<E> {
        int addCount = 0;
        @Override public boolean add(E e) { addCount++; return super.add(e); }
        @Override public boolean addAll(Collection<? extends E> c) { addCount += c.size(); return super.addAll(c); }
    }
    // addAll(List.of("a", "b", "c")) leaves addCount at 6, not 3
    ```

    Internally, `HashSet.addAll` calls `add` once per item, so every item is counted twice. Nothing in the documentation promises or forbids this, so the subclass broke because of a hidden detail inside its parent. Wrapping a `Set` and forwarding calls to it (composition) avoids the problem, because the wrapper no longer depends on how `HashSet` works inside. That wrapping technique is the *Decorator* pattern, covered in **Basics 3 (Creational & Structural Design Patterns)**.

!!! question "Practice"
    Some older Java code declares `class Stack<E> extends ArrayList<E>`. Why is that a poor design?

??? success "Answer"
    A stack should only allow adding and removing items at the top. By extending `ArrayList`, the stack also inherits methods such as `add(index, item)` and `remove(index)`, so any caller can insert or remove items in the middle and break the stack's main rule. A stack is not really a list. It should *have* a private list and expose only `push`, `pop`, and `peek`.

---

## 3. Coupling and cohesion (Level 5)

![Quadrant of coupling against cohesion with the modular quadrant as the goal](assets/topic-02/coupling_cohesion.png)

Coupling and cohesion are the two measurements behind almost every design principle.

- **Cohesion** asks whether the code inside one class belongs together. A class has high cohesion when everything in it serves one purpose and changes for the same reason.
- **Coupling** asks how much one class knows about another. Two classes are tightly coupled when a change in one forces a change in the other.

The goal is the green quadrant: high cohesion and low coupling, so that every change stays local. The original `CheckoutManager` sits in the red quadrant. It mixes Redis, Postgres, discount rules, Stripe, and email in one class (low cohesion), and it creates those dependencies directly, so it is welded to all of them (high coupling). After Levels 1 to 4, each class has one job, and classes talk to each other only through small interfaces such as `CartRepository` and `DiscountRule`.

A practical habit that reduces coupling is **"tell, don't ask"**: instead of pulling data out of an object to make a decision elsewhere, ask the object that owns the data to make the decision.

```java
// Ask: the caller digs into the order's internals and makes the decision itself
if (order.getCustomer().getAddress().getCountry().equals("IN")) { applyDomesticShipping(order); }

// Tell: the order owns its shipping details, and the caller only states what it wants to know
if (order.isDomesticShipment()) { applyDomesticShipping(order); }
```

A long chain of getters is coupling you can see. If the way addresses are stored ever changes, every caller with a chain like that breaks. This guideline is also known as the *Law of Demeter*: talk to the objects you hold directly, not to the objects inside them.

??? info "Go deeper (optional): the kinds of coupling, from worst to best"
    | Kind of coupling | What it looks like |
    |---|---|
    | Content coupling | One class reaches directly into another class's private fields or internal workings. |
    | Global coupling | Classes share mutable global state, which hides dependencies and makes test results depend on the order the tests run in. |
    | Control coupling | A caller passes a flag that tells the method *what to do*, so the caller must understand how the method works inside. |
    | Stamp coupling | A method receives a whole object, such as a `Cart`, when it only needs one value from it, such as its total. |
    | Data coupling | A method receives exactly the values it needs and nothing more. This is the goal. |

!!! question "Practice"
    How would you reduce the coupling in this line?

    ```java
    if (order.getCustomer().getAddress().getCountry().equals("IN")) { applyDomesticShipping(order); }
    ```

??? success "Answer"
    Move the question to the object that owns the data, for example `if (order.isDomesticShipment())`. The order (or the customer it holds) decides how to answer, and the caller no longer depends on how customers, addresses, and countries are structured.

---

## 4. SOLID, one letter at a time (Level 6)

![Five SOLID principles framed as questions about change](assets/topic-02/solid_principles.png)

SOLID is a set of five guidelines for keeping change local. Each letter is best remembered as a question you ask about your code, and each one has a typical symptom, or *smell*, that tells you it is being broken. The sections below apply each letter to the cart and checkout flow.

### S: Single Responsibility

**A class should have only one reason to change.** The useful way to apply this is to ask *who* would ask for the class to change.

The original `CheckoutManager` is changed by five different groups: the product team adds discount rules, the trust and safety team tightens fraud checks, the payments team changes which payment provider is used, the infrastructure team changes how carts are stored and cached, and the fulfillment team changes what happens after an order is placed. Their edits collide in one file. The fix gives each group its own classes, and keeps one small class that coordinates them:

```java
final class PercentageOffRule implements DiscountRule { ... }                    // product team
final class FraudChecker { boolean isSuspicious(Cart cart, Card card) { ... } }   // trust and safety team
final class StripePaymentProcessor implements PaymentProcessor { ... }           // payments team
final class PostgresCartRepository implements CartRepository { ... }             // infrastructure team
final class OrderEventPublisher { void publish(Order order) { ... } }            // fulfillment team
final class CheckoutService { /* coordinates the others, shown in section 6 */ }
```

**Trap:** single responsibility does not mean "one method per class". Methods that protect the same rule belong together. Splitting them across many files scatters one rule, which is the opposite of the goal.

### O: Open/Closed

**A class should be open for extension but closed for modification.** In plain words, a new case should arrive as a new class, without editing code that is already tested.

Levels 3 and 4 already achieved this for discounts. When marketing asks for a "spend MX$1,000, get MX$150 off" rule, we write a `SpendThresholdRule` class. `Cart`, the other rules, and the service that prices a cart are not edited.

**Trap:** only build extension points for changes you have real evidence for. The product team keeps asking for new discount types, so a rule extension point is justified. Adding extension points for changes nobody has asked for, such as pluggable currencies, is guessing, and that breaks YAGNI (Level 7).

### L: Liskov Substitution

**Any implementation must be usable wherever its interface is expected, without surprising the caller.** Matching the method signatures is the easy part. What matters is that every implementation *behaves* the way the contract promises.

Every order needs an order ID, so the service depends on an interface whose contract makes one promise:

```java
interface OrderIdGenerator {
    OrderId next();          // contract: never returns an ID that has already been used
}
```

`SequentialOrderIdGenerator`, which turns an ever-increasing counter into an order ID, keeps that promise. Now imagine a `RandomOrderIdGenerator` that picks random digits and never checks whether the ID is already taken. It compiles and passes a quick test. But because of the *birthday paradox*, a repeated ID becomes likely far sooner than intuition suggests once order volume climbs. When it happens, `save` overwrites someone else's order, and their receipt and payment record get mixed up with another customer's. That generator cannot be safely substituted for an `OrderIdGenerator`. A correct random generator checks whether the ID exists and tries again, which keeps the promise.

The other common symptom is a method that an implementation cannot support. Suppose a team adds `ReadOnlyCartRepository`, which reads from a read-only replica and throws `UnsupportedOperationException` from `save`. Any caller that trusts the `CartRepository` interface would crash. The fix is to model capabilities honestly: give read-only callers a separate `CartReader` interface that contains only `findById`.

The classic interview example is `Square extends Rectangle`. Code that sets a rectangle's width and then its height expects both values to stick, but a square must keep its sides equal, so it silently changes the other side and surprises the caller.

??? info "Go deeper (optional): the four formal substitution rules"
    | Rule | Meaning | Violation example |
    |---|---|---|
    | Preconditions | An implementation cannot demand more from callers than the interface does. | The interface accepts any cart with at least one item, but one implementation rejects carts over 20 items. |
    | Postconditions | An implementation cannot promise less than the interface does. | The interface promises an ID that was never used before, but one generator sometimes returns a duplicate. |
    | Invariants | An implementation must keep every rule the interface keeps true. | A `Square` breaks the rectangle rule that width and height can change independently. |
    | Exceptions | An implementation cannot add new ways to fail. | The interface never throws from `save` for a valid order, but a read-only implementation throws `UnsupportedOperationException`. |

### I: Interface Segregation

**No caller should be forced to depend on methods it does not use.** Interfaces should be shaped around what each kind of caller actually needs.

Suppose `CartRepository` grew over time to include everything anyone asked for:

```java
// Too big: checkout only calls findById and save, but every implementation must provide everything
interface CartRepository {
    Optional<Cart> findById(CartId id);
    void save(Cart cart);
    List<Order> topOrders(int limit);                              // only the dashboards need this
    Map<String, Money> revenueByCountry();                         // only the dashboards need this
}

// Better: small interfaces, one per kind of caller
interface CartRepository { Optional<Cart> findById(CartId id); void save(Cart cart); }
interface OrderStats     { List<Order> topOrders(int limit); Map<String, Money> revenueByCountry(); }
```

Basics 1 already put the durable order store behind its own boundary, separate from the cache, and the interfaces now follow the same split. The checkout path depends only on `CartRepository`, so it is not affected when the analytics team changes its dashboards, and the in-memory fake used in tests no longer has to pretend to compute revenue by country.

**Trap:** split interfaces by what callers need, not mechanically by method. A codebase where every interface has exactly one method is just as hard to work with as one giant interface.

### D: Dependency Inversion

**Business logic should depend on interfaces it owns, not on concrete infrastructure.** Infrastructure, such as databases and third-party services, then plugs in behind those interfaces.

The original `CheckoutManager` creates `new StripeClient(STRIPE_KEY)` itself. That welds the business logic to Stripe, makes it impossible to test without hitting a real payment provider, and means adding a second provider for a new region requires editing the business logic. The fix is to depend on a `PaymentProcessor` interface and receive the implementation from outside, through the constructor:

```java
interface PaymentProcessor {
    PaymentResult charge(Card card, Money amount);     // contract: throws PaymentDeclinedException, never returns a fake success
}

final class CheckoutService {
    private final PaymentProcessor payments;

    CheckoutService(PaymentProcessor payments) {        // handed in, never created here
        this.payments = payments;
    }
}
// In production, the wiring passes a StripePaymentProcessor. In tests, it passes a FakePaymentProcessor
// that never calls a real network, so tests stay fast and never accidentally charge a real card.
```

The diagram shows the change. Before, the business logic points at Postgres. After, both the real repository and an in-memory test fake point up at an interface that belongs to the business logic. The same shape applies here: before, `CheckoutService` points at Stripe; after, both `StripePaymentProcessor` and `FakePaymentProcessor` point up at a `PaymentProcessor` interface that the checkout logic owns.

![Dependency inversion: before, the checkout service depends on Stripe; after, both processors depend on a policy-owned interface](assets/topic-02/dependency_inversion.png)

**Trap:** the interface must be shaped by what the business logic needs, such as `charge(card, amount)`, not copied from one vendor's SDK, such as `createPaymentIntentWithIdempotencyKey(...)`. An interface that mirrors one vendor adds a layer without removing the dependency. Also note that *dependency injection* (passing dependencies in through the constructor) is just the technique used to wire this design; the principle is about which way the dependency points.

!!! question "Practice: which SOLID letter does each snippet break?"
    1. `class InvoiceService { Money calculate(...); void saveToDatabase(...); void emailPdf(...); }`
    2. A `discount(Customer c)` method with an `if / else if` branch for every customer tier, and marketing adds a new tier every quarter.
    3. `class ReadOnlyFile extends File { @Override void write(byte[] data) { throw new UnsupportedOperationException(); } }`
    4. `interface Printer { void print(); void scan(); void fax(); }`, where the `BasicPrinter` implementation throws on `scan` and `fax`.
    5. `class ReportService { private final PostgresClient db = new PostgresClient("prod-db-host"); }`

??? success "Answer"
    1. **Single Responsibility.** Calculating a price, saving to a database, and emailing a PDF are three different reasons to change, owned by three different concerns.
    2. **Open/Closed.** A new tier means editing the branch. Replace it with a `DiscountPolicy` interface and one implementation per tier.
    3. **Liskov Substitution.** A `ReadOnlyFile` cannot honor the `File` contract, which allows writing. It should not extend `File` at all.
    4. **Interface Segregation.** `BasicPrinter` is forced to implement methods it cannot support. Split `Printer` into `Print`, `Scan`, and `Fax` interfaces.
    5. **Dependency Inversion.** The service creates its own database client instead of depending on an interface it owns.

---

## 5. DRY, KISS, and YAGNI (Level 7)

![DRY, KISS, and YAGNI pulling from opposite ends of the abstraction spectrum](assets/topic-02/clean_code_guardrails.png)

SOLID tells you *where* responsibilities should go. These three guidelines tell you *how much* abstraction to build. They pull in opposite directions, and good design sits in the middle.

### DRY: Don't Repeat Yourself

**Every piece of knowledge should have one owner.** If the same business rule is written in several places, the copies eventually drift apart.

Suppose the tax rate for a region is computed separately in three places: checkout, the invoice PDF generator, and the admin refund tool. If a tax rate changes and one copy is missed, a customer's refund is computed with the wrong rate while their original charge used the right one, and nothing fails loudly. A single `TaxCalculator` class that owns the rate table and the calculation gives that knowledge one home.

**Trap:** DRY is about duplicated *knowledge*, not duplicated *text*. Two methods that look identical but belong to different owners, such as checkout validation and fraud-review validation, should stay separate. If you merge them, the first requirement that applies to only one of them adds a boolean flag, and then another. As Sandi Metz put it, "duplication is far cheaper than the wrong abstraction". A useful tie-breaker is the **rule of three**: tolerate a second copy, and extract a shared abstraction when a third copy appears.

### KISS: Keep It Simple

**Every layer of complexity must buy a capability you actually need.** With three discount rules, it can be tempting to build a plugin framework that discovers rule classes automatically and sorts them by priority. The plain list of rules from Level 4 already does the job, and anyone can read it in seconds.

**Trap:** KISS removes complexity that the design added by accident. It does not mean ignoring complexity that is genuinely part of the problem, such as rounding rules for tax or currency conversion. Flattening real rules into something that looks simple but handles edge cases wrongly is a bug.

### YAGNI: You Aren't Gonna Need It

**Do not build for a future that nobody has asked for.** The `CartRepository` interface is worth having today: it costs one small file, and it lets us test with an in-memory store. Building currency conversion or split-tender payments "just in case" is not worth it. Basics 1 explicitly put those out of scope: even though the platform serves four countries, every order is priced and paid in exactly one currency, so `Money` carrying a currency code is enough. Code written against guessed requirements is usually wrong by the time the real need arrives. Keep the extension points that are cheap and proven, but do not build the extensions early.

!!! question "Practice"
    The checkout flow and the fraud-review flow each contain an identical 10-line method that validates a shipping address. A teammate wants to merge them into one shared method. What should you consider?

??? success "Answer"
    Ask whether the two methods share the same *knowledge* or only look the same today. The two flows are owned by different teams and follow different rules: fraud review is usually driven by risk policy, while checkout is driven by product and shipping-carrier requirements. They are likely to diverge, so keeping them separate is often the better choice. If the rule really is shared, for example a single company-wide definition of a well-formed postal address, then extract that one rule into its own class and let both flows use it.

---

## 6. Putting it together: the cart and checkout classes

After all seven levels, the messy `CheckoutManager` has become a set of small classes, each with one clear job:

![Cart and checkout class diagram with policy above and replaceable implementations below a boundary](assets/topic-02/checkout_service_architecture.png)

The dashed line in the diagram separates stable business logic (above) from details that change more often (below). The classes above the line never mention Postgres, Redis, or a particular payment provider, so the store and the payment processor can both be replaced without editing them.

| Class | What it is responsible for | Who asks for it to change |
|---|---|---|
| `Money` | It holds one valid, non-negative amount with a currency. | Rarely anyone, unless currency rules change. |
| `Cart` | It holds one valid cart with its discount rules, and computes the final total. | Rarely anyone, because new discounts arrive as new rules. |
| `DiscountRule` and its rules (`PercentageOffRule`, `FreeShippingRule`, `BogoRule`) | Each rule adjusts a price by one well-defined amount. | The product team, when discounts are added or changed. |
| `OrderIdGenerator` and `SequentialOrderIdGenerator` | It produces an order ID that has never been used before. | The engineering team, when the ID scheme changes. |
| `CartRepository` and `PostgresCartRepository` | It stores carts and finds them by ID. | The infrastructure team, when storage changes. |
| `FraudChecker` | It flags carts that look like stolen-card fraud before they are charged. | The trust and safety team. |
| `PaymentProcessor` and `StripePaymentProcessor` | It charges a card and reports whether the charge succeeded. | The payments team, when a provider changes or a new one is added. |
| `OrderEventPublisher` | It publishes an "order placed" event to the queue from Basics 1. | The fulfillment team. |
| `CheckoutService` | It coordinates the others for the one main flow: turning a priced cart into a paid order. | Anyone who changes that overall workflow. |

The coordinating class is now short, and it contains no storage, payment-provider, or discount-rule details of its own:

```java
final class CheckoutService {
    private final CartRepository carts;
    private final FraudChecker fraud;
    private final PaymentProcessor payments;
    private final OrderIdGenerator orderIds;
    private final OrderEventPublisher events;
    // The constructor receives all five dependencies, exactly as in the Dependency Inversion section.

    CheckoutResult checkout(CartId cartId, Card card) {
        Optional<Cart> found = carts.findById(cartId);
        if (found.isEmpty()) return CheckoutResult.cartNotFound();

        Cart cart = found.get();
        if (fraud.isSuspicious(cart, card)) return CheckoutResult.declined();

        Money total = cart.total();
        PaymentResult payment = payments.charge(card, total);          // throws on failure, per the PaymentProcessor contract
        Order order = new Order(orderIds.next(), cart, total, payment);
        events.publish(order);                                         // async: email, inventory, and loyalty happen later
        return CheckoutResult.success(order);
    }
}
```

The real test of a design is how it handles change. Here is what each likely change request touches:

| Change request | What you edit | What you add | What stays untouched |
|---|---|---|---|
| Add a "buy one, get one" promotion. | You edit only the API code that creates carts with the new rule. | You add a `BogoRule` class. | `Cart`, `CheckoutService`, and every other rule stay untouched. |
| Put a cache in front of the cart store. | You edit only the wiring. | You add a caching repository class, as shown in Basics 3. | `CheckoutService` and `PostgresCartRepository` stay untouched. |
| Switch from sequential order IDs to ULIDs. | You edit only the wiring. | You add a `UlidOrderIdGenerator`. | Every other class stays untouched. |
| Add a new fraud signal, such as flagging mismatched billing and shipping countries. | You edit `FraudChecker`. | You add tests for the new case. | Every other class stays untouched. |
| Let a customer change their shipping address after checkout. | You edit `CheckoutService` and `Order`, because the workflow itself changes. | You add an "update shipping address" flow to the API. | The discount rules, the payment processor, and the repository contract stay untouched. |

The last row is important. Editing a placed order changes a *workflow*, and the coordinating class is supposed to change for workflow reasons. No design absorbs every possible change, and saying so honestly is a stronger answer than claiming the design is open to anything.

??? info "Go deeper (optional): proving substitution with contract tests"
    Level 6 said every implementation must keep its interface's promises. A *contract test* turns those promises into something the build checks. You write the tests once, against the interface, and every implementation's test class inherits them:

    ```java
    abstract class CartRepositoryContractTest {
        protected abstract CartRepository repository();       // each implementation's test supplies one

        @Test void unknownIdIsEmpty() {
            assertTrue(repository().findById(new CartId("missing")).isEmpty());
        }
        @Test void savedCartCanBeFound() {
            CartRepository repository = repository();
            repository.save(sampleCart());
            assertEquals(Optional.of(sampleCart()), repository.findById(sampleCart().id()));
        }
    }
    class InMemoryCartRepositoryTest extends CartRepositoryContractTest { ... }
    class PostgresCartRepositoryTest extends CartRepositoryContractTest { ... }   // runs against a real test database
    ```

    This matters most for fakes. If the in-memory fake behaves differently from Postgres, every test that uses it proves the wrong thing. Running the same suite against both keeps the fake honest. Inheritance is the right tool here, because every concrete test class truly *is* a repository contract test.

---

## 7. Design smells to recognize

![Design smells connected to expensive change](assets/topic-02/design_smells.png)

A *smell* is a visible symptom that a design will make change expensive. Learning to spot these is the fastest way to apply the principles in real code reviews. Each smell below maps to one of the principles on this page.

| Smell | How you notice it | Principle at stake | Usual fix |
|---|---|---|---|
| **God class** | One class is edited in most pull requests, often with a name ending in `Manager`. | Single Responsibility | Split it into one class per group of people that asks for changes. |
| **Type switch** | The same `switch` or `instanceof` check on a type appears in several places. | Open/Closed | Replace the checks with an interface and one implementation per type. |
| **Refused bequest** | A subclass overrides inherited methods just to throw an exception or do nothing. | Liskov Substitution | Stop inheriting, and compose the capabilities that the class really has. |
| **Fat interface** | Implementations are forced to write empty or throwing versions of methods they cannot support. | Interface Segregation | Split the interface into smaller ones shaped around each kind of caller. |
| **Concrete coupling** | Business logic creates databases or provider clients itself with `new`. | Dependency Inversion | Depend on an interface owned by the business logic, and pass the implementation in. |
| **Shotgun surgery** | Changing one business rule means editing many files. | DRY | Move that knowledge into one owner that every other class uses. |

!!! warning "Refactor because of evidence, not taste"
    "This could be cleaner" is not a strong reason to restructure code. "This rule changed three times, and we missed one copy twice" is. Name the change that hurts, and make the smallest structural change that keeps it local.

---

## 8. Test yourself

These three problems increase in difficulty. Try each one on paper before opening the answer.

!!! question "Problem 1 (warm-up): a user profile"
    ```java
    class User {
        public String email;
        private int age;
        public void setAge(int age) { this.age = age; }
    }
    ```
    Which principle does this break, and how would you fix it?

??? success "Answer"
    It breaks **encapsulation**. The `email` field is public, so anyone can set it to an invalid value, and `setAge` accepts negative ages. Make the fields private and final, validate both values once in the constructor (or in an `Email` type that validates itself), and only allow changes through methods that enforce the rules, such as `changeEmail(Email newEmail)`.

!!! question "Problem 2 (code review): a report generator"
    ```java
    class ReportGenerator extends PostgresConnection {
        String generate(String format) {
            if (format.equals("PDF")) { /* build a PDF from query results */ }
            else if (format.equals("CSV")) { /* build a CSV from query results */ }
            ...
        }
    }
    ```
    This class has three separate problems. Name each one, the principle it breaks, and the fix.

??? success "Answer"
    1. **Inheriting to reuse code.** A report generator is not a database connection; it only *uses* one. Extending `PostgresConnection` exposes every connection method on the generator. Use composition: the generator should *have* a data source.
    2. **A type switch on the format** breaks Open/Closed, because every new format edits this method. Give each format its own class behind a `ReportFormatter` interface.
    3. **Concrete coupling to Postgres** breaks Dependency Inversion, because the generator cannot be tested without a real database. Depend on a small `ReportData` interface shaped around what the report needs, and pass the Postgres implementation in from outside.

!!! question "Problem 3 (design): a logging library"
    Design the main classes for a logging library. Logs can be written to the console, a file, or a remote server, and each log line can be formatted as plain text or JSON. New destinations and formats are expected in the future.

??? success "Answer"
    The tempting inheritance design creates a class for every combination, such as `ConsoleJsonLogger` and `FilePlainLogger`. Three destinations and two formats already need six classes, and every new format adds three more.

    Composition keeps the two kinds of variation independent:

    ```java
    interface Formatter   { String format(LogEvent event); }          // PlainFormatter, JsonFormatter
    interface Destination { void write(String line); }                // ConsoleDestination, FileDestination, RemoteDestination

    final class Logger {
        private final Formatter formatter;
        private final List<Destination> destinations;
        // The constructor receives the formatter and the destinations from outside.

        void log(LogEvent event) {
            String line = formatter.format(event);
            for (Destination destination : destinations) destination.write(line);
        }
    }
    ```

    A new format is one new `Formatter` class, and a new destination is one new `Destination` class, with no combinations to multiply. Each class has a single responsibility, the `Logger` depends only on interfaces (Dependency Inversion), and tests can pass in a fake destination that simply records lines.

---

## 9. How this shows up in an LLD interview

![Six-stage low-level design interview framework](assets/topic-02/lld_interview_framework.png)

A low-level design (LLD) interview asks you to design the classes for a small system, and often to write the core code. It follows the same funnel as the system design interview in Basics 1, one level closer to the code.

| Stage | What you are trying to achieve |
|---|---|
| Clarify | Agree on the main use cases, say what is out of scope, and name one or two changes that are likely to come. |
| Model | List the main classes, and give each one a single-sentence responsibility. |
| Contract | Define the key interfaces and the rules each object guarantees. |
| Relate | Draw a class diagram that shows which classes have, implement, or depend on which others. |
| Code | Write the main flow in real code, including at least one failure case. |
| Extend | Walk through a likely change and show that it becomes a new class rather than an edit to existing code. |

!!! tip "The LLD round in one sentence"
    Find the changes that are likely to come, give each one a single owner behind a small interface, and show that a new requirement becomes a new class rather than an edit.

### Checklist

```text
[ ] Keep each object's data private, and enforce its rules in one place.
[ ] Let callers depend on what an object does, not on how it does it.
[ ] Replace repeated type switches with an interface and one class per type.
[ ] Use composition for capabilities; use inheritance only for a true, stable is-a.
[ ] Aim for high cohesion inside classes and low coupling between them.
[ ] Check each SOLID question: who changes it, can it extend, can it substitute,
    does each caller use the whole interface, and can it run without real infrastructure?
[ ] Apply DRY to knowledge, KISS to mechanisms, and YAGNI to guesses about the future.
[ ] Show how a likely change becomes a new class, and admit which changes the design does not absorb.
```

### What comes next

| Topic you may have heard about | Where it is covered |
|---|---|
| Factory, Builder, Singleton, Adapter, Decorator, and other structural patterns, applied to these same cart and checkout classes | Basics 3: Creational & Structural Design Patterns |
| Strategy (the pattern behind `DiscountRule` and `OrderIdGenerator`), Observer, Template Method, and other behavioral patterns | Advanced 1: Behavioral Design Patterns |
| Full machine-coding case studies, such as a parking lot or a ticket booking system | Advanced 2: Real-World Machine Coding Case Studies |
| Service boundaries, modular monoliths, and microservices | Basics 5: Architecture Styles & Service Decomposition |
| Cache strategies, expiry, and eviction | Basics 9: Caching Core |
| Queues that process order-placed events in the background | Basics 13: Asynchronous Processing Basics |
| Generating unique order IDs across many servers at once | Basics 15: Distributed ID Generation |
