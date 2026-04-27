#!/usr/bin/env python3
"""
Semantic Product Comparison System - SPARQL Queries
Loads Protégé-exported OWL ontology and runs SPARQL queries with CSV export.
"""

import sys
from pathlib import Path
from colorama import init, Fore, Style

try:
    from rdflib import Graph, Namespace
    from SPARQLWrapper import SPARQLWrapper, JSON
    import pandas as pd
    from tabulate import tabulate
except ImportError as e:
    print(f"{Fore.RED}Error: Missing required package.{Style.RESET_ALL}")
    print(f"Run: pip install rdflib SPARQLWrapper pandas tabulate colorama")
    sys.exit(1)

init(autoreset=True)

# Configuration
ONTOLOGY_FILE = Path("ontology/products_reasoned.owl")
DATA_DIR = Path("data")
PC = Namespace("http://www.semanticweb.org/productcomparison#")

def print_banner(text):
    """Print a colored banner."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def load_ontology():
    """Load the OWL ontology into an RDF graph."""
    if not ONTOLOGY_FILE.exists():
        print(f"{Fore.YELLOW}Warning: {ONTOLOGY_FILE} not found.{Style.RESET_ALL}")
        print("Please export your Protégé ontology to ontology/products_reasoned.owl")
        return None
    
    g = Graph()
    try:
        g.parse(str(ONTOLOGY_FILE), format="xml")
        print(f"{Fore.GREEN}✓ Loaded {len(g)} triples from {ONTOLOGY_FILE}{Style.RESET_ALL}")
        return g
    except Exception as e:
        print(f"{Fore.RED}✗ Error loading ontology: {e}{Style.RESET_ALL}")
        return None

def run_query(graph, query, name):
    """Run a SPARQL query and return results as a list of dicts."""
    try:
        results = list(graph.query(query))
        return results
    except Exception as e:
        print(f"{Fore.RED}✗ Query '{name}' failed: {e}{Style.RESET_ALL}")
        return []

def print_results(results, headers, title):
    """Print query results as a formatted table."""
    if not results:
        print(f"{Fore.YELLOW}No results for {title}{Style.RESET_ALL}")
        return
    
    rows = [[str(val) for val in row] for row in results]
    print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=[25]*len(headers)))
    print(f"\n{Fore.GREEN}Found {len(results)} results{Style.RESET_ALL}")

def main():
    print_banner("SEMANTIC PRODUCT COMPARISON SYSTEM")
    
    # Load ontology
    graph = load_ontology()
    if not graph:
        print(f"\n{Fore.YELLOW}Continuing without ontology file...{Style.RESET_ALL}")
        return
    
    DATA_DIR.mkdir(exist_ok=True)
    all_results = {}
    
    # =========================================================================
    # QUERY A: All products ranked by score
    # =========================================================================
    print_banner("QUERY A: Products Ranked by Score")
    query_a = """
    PREFIX pc: <http://www.semanticweb.org/productcomparison#>
    SELECT ?name ?price ?score WHERE {
        ?p pc:hasName ?name ;
           pc:hasPrice ?price ;
           pc:hasScore ?score .
    }
    ORDER BY DESC(?score)
    """
    results_a = run_query(graph, query_a, "Query A")
    print_results(results_a, ["Product Name", "Price ($)", "Score"], "Products by Score")
    all_results['A'] = results_a
    
    # =========================================================================
    # QUERY B: Products with inferred tags (from SWRL rules)
    # =========================================================================
    print_banner("QUERY B: Products with Inferred Tags")
    query_b = """
    PREFIX pc: <http://www.semanticweb.org/productcomparison#>
    SELECT ?name ?tag WHERE {
        ?p pc:hasName ?name ;
           pc:hasTag ?tag .
    }
    """
    results_b = run_query(graph, query_b, "Query B")
    print_results(results_b, ["Product Name", "Tag"], "Inferred Tags")
    all_results['B'] = results_b
    
    # =========================================================================
    # QUERY C: isBetterThan relationships
    # =========================================================================
    print_banner("QUERY C: isBetterThan Relationships")
    query_c = """
    PREFIX pc: <http://www.semanticweb.org/productcomparison#>
    SELECT ?better ?worse WHERE {
        ?a pc:isBetterThan ?b ;
           pc:hasName ?better .
        ?b pc:hasName ?worse .
    }
    """
    results_c = run_query(graph, query_c, "Query C")
    print_results(results_c, ["Better Product", "Worse Product"], "Comparison Pairs")
    all_results['C'] = results_c
    
    # =========================================================================
    # QUERY D: Budget picks (under $500, score > 55)
    # =========================================================================
    print_banner("QUERY D: Budget Picks (Under $500, Score > 55)")
    query_d = """
    PREFIX pc: <http://www.semanticweb.org/productcomparison#>
    SELECT ?name ?price ?score WHERE {
        ?p pc:hasName ?name ;
           pc:hasPrice ?price ;
           pc:hasScore ?score .
        FILTER(?price < 500 && ?score > 55)
    }
    ORDER BY DESC(?score)
    """
    results_d = run_query(graph, query_d, "Query D")
    print_results(results_d, ["Product Name", "Price ($)", "Score"], "Budget Picks")
    all_results['D'] = results_d
    
    # =========================================================================
    # QUERY E: ASK - Is iPhone 15 Pro better than iPhone 14?
    # =========================================================================
    print_banner("QUERY E: ASK Query")
    query_e = """
    PREFIX pc: <http://www.semanticweb.org/productcomparison#>
    ASK WHERE {
        pc:iPhone15Pro pc:isBetterThan pc:iPhone14 .
    }
    """
    ask_result = bool(graph.query(query_e))
    print(f"\nIs {Fore.CYAN}iPhone 15 Pro{Style.RESET_ALL} better than {Fore.CYAN}iPhone 14{Style.RESET_ALL}?")
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}Answer: {ask_result}{Style.RESET_ALL}\n")
    all_results['E'] = [(str(ask_result),)]
    
    # =========================================================================
    # TASK 2: Wikidata Linked Data Enrichment
    # =========================================================================
    print_banner("LINKED DATA: Brand Info from Wikidata")
    try:
        wikidata = SPARQLWrapper("https://query.wikidata.org/sparql")
        wikidata.setQuery("""
        SELECT ?brand ?foundingYear ?country WHERE {
          VALUES ?brand { wd:Q312 wd:Q20656 wd:Q2283 }
          OPTIONAL { ?brand wdt:P571 ?foundingYear }
          OPTIONAL { ?brand wdt:P17 ?countryObj . ?countryObj rdfs:label ?country . FILTER(LANG(?country) = "en") }
        }
        """)
        wikidata.setReturnFormat(JSON)
        wiki_results = wikidata.query().convert()
        
        rows = []
        for result in wiki_results["results"]["bindings"]:
            brand = result.get("brand", {}).get("value", "").split("/")[-1]
            year = result.get("foundingYear", {}).get("value", "N/A")[:4] if result.get("foundingYear") else "N/A"
            country = result.get("country", {}).get("value", "N/A")
            rows.append([brand, year, country])
        
        print(tabulate(rows, headers=["Wikidata ID", "Founding Year", "Country"], tablefmt="grid"))
        print(f"\n{Fore.GREEN}✓ Retrieved brand data from Wikidata{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Wikidata query failed: {e}{Style.RESET_ALL}")
    
    # =========================================================================
    # TASK 3: Export to CSV
    # =========================================================================
    print_banner("EXPORTING RESULTS TO CSV")
    csv_path = DATA_DIR / "query_results.csv"
    
    try:
        df_rows = []
        for query_key, results in all_results.items():
            for row in results:
                df_rows.append({
                    'query_id': query_key,
                    'col1': str(row[0]) if len(row) > 0 else '',
                    'col2': str(row[1]) if len(row) > 1 else '',
                    'col3': str(row[2]) if len(row) > 2 else ''
                })
        
        df = pd.DataFrame(df_rows)
        df.to_csv(csv_path, index=False)
        print(f"{Fore.GREEN}✓ Results saved to {csv_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Export failed: {e}{Style.RESET_ALL}")
    
    # =========================================================================
    # TASK 4: Interactive Product Comparison
    # =========================================================================
    print_banner("INTERACTIVE PRODUCT COMPARISON")
    
    try:
        name_a = input(f"{Fore.CYAN}Enter Product A name (or press Enter to skip): {Style.RESET_ALL}").strip()
        if not name_a:
            print(f"{Fore.YELLOW}Skipping interactive comparison.{Style.RESET_ALL}")
            return
        
        name_b = input(f"{Fore.CYAN}Enter Product B name: {Style.RESET_ALL}").strip()
        if not name_b:
            print(f"{Fore.YELLOW}Please enter both product names.{Style.RESET_ALL}")
            return
        
        # Find products in graph
        query_find = """
        PREFIX pc: <http://www.semanticweb.org/productcomparison#>
        SELECT ?p ?type WHERE {
            ?p pc:hasName ?name .
            OPTIONAL { ?p rdf:type ?type }
            FILTER(CONTAINS(LCASE(?name), LCASE("%s")) || CONTAINS(LCASE(%s), LCASE(?name)))
        }
        """ % (name_a, "'" + name_a + "'")
        
        # Simple lookup by exact name match
        def find_product(name):
            query = f"""
            PREFIX pc: <http://www.semanticweb.org/productcomparison#>
            SELECT ?p WHERE {{
                ?p pc:hasName "{name}" .
            }}
            """
            results = list(graph.query(query))
            return results[0][0] if results else None
        
        product_a = find_product(name_a)
        product_b = find_product(name_b)
        
        if not product_a or not product_b:
            print(f"{Fore.RED}✗ One or both products not found in ontology.{Style.RESET_ALL}")
            return
        
        # Get specs for both products
        def get_specs(product_uri):
            query = f"""
            PREFIX pc: <http://www.semanticweb.org/productcomparison#>
            SELECT ?price ?ram ?storage ?score ?battery ?type WHERE {{
                <{product_uri}> pc:hasPrice ?price ;
                                pc:hasRAM ?ram ;
                                pc:hasStorage ?storage ;
                                pc:hasScore ?score .
                OPTIONAL {{ <{product_uri}> pc:hasBatteryLife ?battery }}
                OPTIONAL {{ <{product_uri}> rdf:type ?type }}
            }}
            """
            results = list(graph.query(query))
            if results:
                row = results[0]
                return {
                    'price': float(row[0]),
                    'ram': int(row[1]),
                    'storage': int(row[2]),
                    'score': float(row[3]),
                    'battery': float(row[4]) if row[4] else None,
                    'type': str(row[5]).split('#')[-1] if row[5] else ''
                }
            return None
        
        specs_a = get_specs(str(product_a))
        specs_b = get_specs(str(product_b))
        
        if not specs_a or not specs_b:
            print(f"{Fore.RED}✗ Could not retrieve specs for one or both products.{Style.RESET_ALL}")
            return
        
        # Build comparison table
        print(f"\n{Fore.CYAN}{Style.BRIGHT}COMPARISON: {name_a} vs {name_b}{Style.RESET_ALL}\n")
        
        comparison_rows = []
        
        # Price (lower is better)
        winner_price = name_a if specs_a['price'] < specs_b['price'] else name_b
        comparison_rows.append([
            "Price ($)", 
            f"${specs_a['price']:.2f}", 
            f"${specs_b['price']:.2f}",
            f"{Fore.GREEN}{winner_price} (lower){Style.RESET_ALL}"
        ])
        
        # RAM (higher is better)
        winner_ram = name_a if specs_a['ram'] > specs_b['ram'] else name_b
        comparison_rows.append([
            "RAM (GB)", 
            str(specs_a['ram']), 
            str(specs_b['ram']),
            f"{Fore.GREEN}{winner_ram} (higher){Style.RESET_ALL}"
        ])
        
        # Storage (higher is better)
        winner_storage = name_a if specs_a['storage'] > specs_b['storage'] else name_b
        comparison_rows.append([
            "Storage (GB)", 
            str(specs_a['storage']), 
            str(specs_b['storage']),
            f"{Fore.GREEN}{winner_storage} (higher){Style.RESET_ALL}"
        ])
        
        # Score (higher is better)
        winner_score = name_a if specs_a['score'] > specs_b['score'] else name_b
        comparison_rows.append([
            "Score", 
            str(specs_a['score']), 
            str(specs_b['score']),
            f"{Fore.GREEN}{winner_score} (higher){Style.RESET_ALL}"
        ])
        
        # Battery (only for smartphones)
        is_smartphone_a = 'Smartphone' in specs_a.get('type', '')
        is_smartphone_b = 'Smartphone' in specs_b.get('type', '')
        
        if is_smartphone_a and is_smartphone_b and specs_a.get('battery') and specs_b.get('battery'):
            winner_battery = name_a if specs_a['battery'] > specs_b['battery'] else name_b
            comparison_rows.append([
                "Battery Life (hrs)", 
                f"{specs_a['battery']:.1f}", 
                f"{specs_b['battery']:.1f}",
                f"{Fore.GREEN}{winner_battery} (higher){Style.RESET_ALL}"
            ])
        
        print(tabulate(
            comparison_rows, 
            headers=["Spec", name_a, name_b, "Winner"], 
            tablefmt="grid"
        ))
        
        # Overall recommendation
        a_wins = sum([
            specs_a['price'] < specs_b['price'],
            specs_a['ram'] > specs_b['ram'],
            specs_a['storage'] > specs_b['storage'],
            specs_a['score'] > specs_b['score']
        ])
        b_wins = 4 - a_wins
        
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}RECOMMENDATION:{Style.RESET_ALL}")
        if a_wins > b_wins:
            print(f"{Fore.GREEN}{name_a} wins {a_wins}-{b_wins} on key specs!{Style.RESET_ALL}")
        elif b_wins > a_wins:
            print(f"{Fore.GREEN}{name_b} wins {b_wins}-{a_wins} on key specs!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}It's a tie! Consider other factors.{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Comparison cancelled.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error in comparison: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
