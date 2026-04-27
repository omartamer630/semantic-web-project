package org.example;

public class Main {
    public static void main(String[] args) {
        // Load your ontology file from src/main/resources/
        ProductComparator comparator = new ProductComparator("product_comparison.ttl");

        System.out.println("=== All Products ===");
        comparator.getAllProducts().forEach(System.out::println);

        System.out.println("\n=== Laptops by RAM Value ===");
        comparator.compareLaptopsByRAM().forEach(System.out::println);

        System.out.println("\n=== Full Comparison ===");
        comparator.getFullComparison().forEach(System.out::println);
    }
}