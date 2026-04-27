# Semantic Product Comparison Ontology Documentation

## 1. Overview
This ontology models electronic products (laptops and smartphones) and their technical specifications to enable **semantic comparison, filtering, and value analysis**. It is designed for a research/academic project demonstrating how RDF/OWL and SPARQL can replace rigid relational schemas with a flexible, query-driven comparison system.

**Core Use Cases:**
- Cross-product specification comparison
- Price-to-performance ratio analysis
- Handling incomplete/heterogeneous spec data
- Category-aware filtering and recommendation logic

---

## 2. Namespace & Prefixes
| Prefix | IRI | Purpose |
|--------|-----|---------|
| `pc:` | `http://www.semanticweb.org/productcomparison#` | Custom ontology namespace |
| `owl:` | `http://www.w3.org/2002/07/owl#` | OWL 2 vocabulary |
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | RDF core vocabulary |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` | RDFS vocabulary |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | XML Schema datatypes |

---

## 3. Class Hierarchy (Taxonomy)
```
pc:Product (root class)
 ├── pc:Laptop
 └── pc:Smartphone

pc:Brand (independent class)
pc:Spec  (independent class)
```
- **Inheritance:** `Laptop` and `Smartphone` are declared as `rdfs:subClassOf pc:Product`, enabling category-based reasoning and SPARQL filtering (`?prod a pc:Laptop`).
- **Independence:** `Brand` and `Spec` are top-level classes linked via object properties, keeping the schema decoupled and extensible.

---

## 4. Property Definitions

### 🔹 Object Properties
| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `pc:hasBrand` | `pc:Product` | `pc:Brand` | Links a product to its manufacturer |
| `pc:hasSpec` | `pc:Product` | `pc:Spec` | Attaches technical specifications to a product |

###  Data Properties
| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `pc:name` | `pc:Product` | `xsd:string` | Human-readable product name |
| `pc:price` | `pc:Product` | `xsd:decimal` | Retail price (numeric for calculations) |
| `pc:specName` | `pc:Spec` | `xsd:string` | Specification identifier (e.g., `"ram"`, `"battery"`) |
| `pc:value` | `pc:Spec` | `xsd:decimal` | Numeric measurement of the spec |
| `pc:unit` | `pc:Spec` | `xsd:string` | Measurement unit (e.g., `"GB"`, `"hours"`, `"inch"`) |

---

## 5. Core Design Pattern: Flexible Specification Modeling
Instead of hardcoding properties like `pc:ram` or `pc:battery`, the ontology uses a **key-value-unit triplet pattern** via the `pc:Spec` class:
```turtle
pc:RAM_Acer a pc:Spec ;
    pc:specName "ram" ;
    pc:value 8 ;
    pc:unit "GB" .
pc:AcerAspire3 pc:hasSpec pc:RAM_Acer .
```

### ✅ Why this pattern?
1. **Heterogeneity Handling:** Laptops and smartphones share some specs (RAM, storage) but differ in others (CPU cores vs camera MP). A unified `Spec` class avoids sparse/nullable columns.
2. **Dynamic Extensibility:** New specs (e.g., `"refresh_rate"`, `"5g_support"`) can be added without modifying the ontology schema.
3. **SPARQL Flexibility:** Enables `OPTIONAL` matching, dynamic pivoting, and cross-category comparison without schema changes.
4. **Academic Alignment:** Mirrors real-world knowledge graph design patterns (e.g., Wikidata, Schema.org `PropertyValue`).

---

## 6. Instance Overview (Sample Data)
### 🏷️ Brands (5)
`Apple`, `Dell`, `Acer`, `Samsung`, `Realme` (each annotated with `rdfs:label` for readable output)

### 📱 Products (6)
| Product | Type | Price |
|---------|------|-------|
| Acer Aspire 3 | Laptop | $449 |
| Dell XPS 15 | Laptop | $1,799 |
| MacBook Pro 16 M3 Pro | Laptop | $2,499 |
| Realme 11 Pro+ | Smartphone | $299 |
| Samsung Galaxy S24 Ultra | Smartphone | $1,299 |
| iPhone 14 | Smartphone | $599 |

### 📊 Specifications per Product
Each product contains **6 standardized specs**:
- Laptops: `ram`, `storage`, `screen`, `battery`, `weight`, `cpu_cores`
- Smartphones: `ram`, `storage`, `screen`, `battery`, `weight`, `camera_mp`

All values use realistic, market-aligned measurements.

---

## 7. Semantic Comparison Capabilities
The ontology natively supports these analytical queries via SPARQL 1.1:

| Capability | SPARQL Pattern | Use Case |
|------------|----------------|----------|
| **Full Comparison Matrix** | `OPTIONAL` + multi-spec pivot | Gracefully handles missing specs |
| **Price/Performance Ratio** | `(?price / ?ram AS ?ratio)` | Identifies "best value" products |
| **Cross-Category Analysis** | `?prod a ?type` + shared spec filter | Compares battery/screen across phones & laptops |
| **Semantic Filtering** | `FILTER(?ram >= 16 && ?price < 2000)` | Recommendation engine logic |
| **Brand Analytics** | `GROUP BY ?brand` + `AVG/MIN/MAX` | Market positioning insights |

---
## 8. Technical Implementation Notes
- **Format:** Turtle (`.ttl`) – human-readable, standard for RDF serialization
- **Loading:** Apache Jena `RDFDataMgr`, Protégé, or any SPARQL endpoint
- **Querying:** SPARQL 1.1 SELECT/CONSTRUCT/ASK supported
- **Performance:** Index-friendly pattern; scales linearly with spec count

---
