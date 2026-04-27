package org.example;

import org.apache.jena.query.*;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.RDFDataMgr;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ProductComparator {

    private final Model model;

    public ProductComparator(String ontologyPath) {
        model = ModelFactory.createDefaultModel();
        // Load from classpath (resources folder)
        InputStream input = getClass().getClassLoader().getResourceAsStream(ontologyPath);
        if (input == null) {
            throw new RuntimeException("Ontology file not found: " + ontologyPath);
        }
        RDFDataMgr.read(model, input, org.apache.jena.riot.Lang.TURTLE);
    }

    /**
     * Run any SPARQL SELECT query and return results as list of maps
     */
    public List<Map<String, Object>> runQuery(String sparql) {
        List<Map<String, Object>> results = new ArrayList<>();
        Query query = QueryFactory.create(sparql);

        try (QueryExecution qexec = QueryExecutionFactory.create(query, model)) {
            ResultSet rs = qexec.execSelect();
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                Map<String, Object> row = new HashMap<>();
                for (String var : rs.getResultVars()) {
                    if (sol.contains(var)) {
                        row.put(var, sol.get(var).isLiteral()
                                ? sol.getLiteral(var).getValue()
                                : sol.getResource(var).getLocalName());
                    }
                }
                results.add(row);
            }
        }
        return results;
    }

    /**
     * Get all products with basic info
     */
    public List<Map<String, Object>> getAllProducts() {
        String query = """
            PREFIX pc: <http://www.semanticweb.org/productcomparison#>
            SELECT ?name ?price ?type
            WHERE {
              ?product a ?type ;
                       pc:name ?name ;
                       pc:price ?price .
            } ORDER BY ?price
            """;
        return runQuery(query);
    }

    /**
     * Compare products by RAM (laptops only)
     */
    public List<Map<String, Object>> compareLaptopsByRAM() {
        String query = """
            PREFIX pc: <http://www.semanticweb.org/productcomparison#>
            SELECT ?name ?ram ?price (?price / ?ram AS ?pricePerGB)
            WHERE {
              ?prod a pc:Laptop ;
                    pc:name ?name ;
                    pc:price ?price ;
                    pc:hasSpec ?spec .
              ?spec pc:specName "ram" ; pc:value ?ram .
            } ORDER BY ASC(?pricePerGB)
            """;
        return runQuery(query);
    }

    /**
     * Full comparison matrix with optional specs
     */
    public List<Map<String, Object>> getFullComparison() {
        String query = """
            PREFIX pc: <http://www.semanticweb.org/productcomparison#>
            SELECT ?name ?type ?ram ?storage ?screen ?battery
            WHERE {
              ?prod pc:name ?name ; a ?type .
              OPTIONAL { ?prod pc:hasSpec ?s1 . ?s1 pc:specName "ram" ; pc:value ?ram . }
              OPTIONAL { ?prod pc:hasSpec ?s2 . ?s2 pc:specName "storage" ; pc:value ?storage . }
              OPTIONAL { ?prod pc:hasSpec ?s3 . ?s3 pc:specName "screen" ; pc:value ?screen . }
              OPTIONAL { ?prod pc:hasSpec ?s4 . ?s4 pc:specName "battery" ; pc:value ?battery . }
            } ORDER BY ?type ?name
            """;
        return runQuery(query);
    }
}