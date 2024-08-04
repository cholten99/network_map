document.addEventListener('DOMContentLoaded', async function() {
    const width = 800;  // Set the width for the SVG
    const height = 600; // Set the height for the SVG

    // Setup SVG container
    const svg = d3.select('#graph').append('svg')
        .attr('width', width)
        .attr('height', height);

    // Node data with placeholders for user data
    const nodes = [
        { id: 1, type: 'circle', userData: null },
        { id: 2, type: 'rectangle', userData: null },
        { id: 3, type: 'triangle', userData: null }
    ];

    // Links between the nodes
    const links = [
        { source: 1, target: 2 },
        { source: 2, target: 3 }
    ];

    // Initialize force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Add links
    const link = svg.selectAll(".link")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke", "#aaa")
        .attr("stroke-width", 2);

    // Create node group and apply the drag behavior
    const node = svg.selectAll(".node")
        .data(nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    node.append("path")
        .attr("d", d => {
            if (d.type === 'rectangle') {
                return 'M -15 -10 15 -10 15 10 -15 10 Z'; // Path for rectangle
            } else if (d.type === 'triangle') {
                return 'M -10 10 10 10 0 -10 Z'; // Path for triangle
            }
            return '';
        })
        .attr("fill", d => {
            if (d.type === 'rectangle') return 'red';
            if (d.type === 'triangle') return 'green';
            return 'none';
        });

    node.append("circle")
        .filter(d => d.type === 'circle')
        .attr("r", 10)
        .attr("fill", "blue");

    // Tooltip setup
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "white")
        .style("padding", "5px")
        .style("border", "1px solid #ccc");

    node.on("mouseover", (event, d) => {
        fetchRandomUser().then(user => {
            d.userData = user;  // Save user data to node
            tooltip.html(`User: ${user.name.first} ${user.name.last}<br>Email: ${user.email}`)
                .style("visibility", "visible")
                .style("top", (event.pageY - 10) + "px")
                .style("left", (event.pageX + 10) + "px");
        });
    })
    .on("mouseout", () => {
        tooltip.style("visibility", "hidden");
    });

    simulation.on("tick", () => {
        // Update link positions
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // Update node positions
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Function to fetch random user data
    async function fetchRandomUser() {
        const url = "https://randomuser.me/api/";
        try {
            const response = await fetch(url);
            const data = await response.json();
            return data.results[0]; // Return the first user in the results array
        } catch (error) {
            console.error('Error fetching user data:', error);
            return null;  // Return null in case of an error
        }
    }
});
