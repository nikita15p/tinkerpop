package com.tinkerpop.tinkergraph.process.olap;

import com.tinkerpop.gremlin.structure.Graph;
import com.tinkerpop.tinkergraph.TinkerFactory;
import com.tinkerpop.tinkergraph.TinkerGraphComputer;
import org.junit.Test;

/**
 * @author Marko A. Rodriguez (http://markorodriguez.com)
 */
public class TinkerGraphComputerTest {

    @Test
    public void testStuff() throws Exception {
        Graph g = TinkerFactory.createClassic();
        //ComputeResult result = g.compute().program(TraversalVertexProgram.create().gremlin(() -> g.V().outE()).build()).submit().get();
        g.V().out().value("name").forEach(System.out::println);
        System.out.println("----------");
        //new TraversalResult<>(g, () -> g.V().out().value("name")).forEachRemaining(System.out::println);

        g.V().out().value("name").submit(g.compute()).forEachRemaining(System.out::println);
    }
}
