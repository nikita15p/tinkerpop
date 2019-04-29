/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.apache.tinkerpop.machine.structure.jdbc;

import org.apache.tinkerpop.machine.strategy.Strategy;
import org.apache.tinkerpop.machine.structure.Structure;
import org.apache.tinkerpop.machine.structure.StructureFactory;
import org.apache.tinkerpop.machine.structure.jdbc.strategy.JDBCStrategy;

import java.util.Map;
import java.util.Set;

/**
 * @author Marko A. Rodriguez (http://markorodriguez.com)
 */
public class JDBCStructure implements StructureFactory {

    private final Map<String, Object> configuration;

    public JDBCStructure(final Map<String, Object> configuration) {
        this.configuration = configuration;
    }

    @Override
    public Set<Strategy<?>> getStrategies() {
        return Set.of(new JDBCStrategy());
    }

    @Override
    public Structure mint() {
        return new JDBCDatabase((String) this.configuration.get("jdbc.connection"));
    }
}