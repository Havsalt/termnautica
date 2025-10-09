use pyo3::prelude::*;

const RESET: &str = "\x1b[0m";

#[pyfunction]
fn render_all(
    screen: &PyAny,
    nodes: &PyAny,
    camera: &PyAny,
    camera_centering_x: f32,
    camera_centering_y: f32,
) -> PyResult<String> {
    let screen_width: u32 = screen.getattr("width")?.extract()?;
    let screen_height: u32 = screen.getattr("height")?.extract()?;
    let camera_position = camera.getattr("global_position")?;
    let mut camera_x: f32 = camera_position.getattr("x")?.extract()?;
    camera_x -= camera_centering_x;
    let mut camera_y: f32 = camera_position.getattr("y")?.extract()?;
    camera_y -= camera_centering_y;
    let transparency_fill: char = screen.getattr("transparency_fill")?.extract()?;
    // Empty 2D screen buffer filled with `screen.transparency_fill`
    let mut screen_buf: Vec<Vec<(char, Option<String>)>> =
        vec![vec![(transparency_fill, None); screen_width as usize]; screen_height as usize];
    let nodes_list: Vec<&PyAny> = nodes.extract()?;
    let mut nodes_z_index_pairs: Vec<_> = nodes_list
        .iter()
        .map(|node| {
            let z_index = node.getattr("z_index").unwrap().extract::<i32>().unwrap();
            (node, z_index)
        })
        .collect();
    nodes_z_index_pairs.sort_unstable_by(|(_, a), (_, b)| a.cmp(b));

    // Render each `TextureNode`
    for (node, _) in nodes_z_index_pairs {
        let is_globally_visible_meth = node.getattr("is_globally_visible")?;
        if !is_globally_visible_meth.call0()?.extract()? {
            continue;
        }
        let global_position = node.getattr("global_position")?;
        let global_x: f32 = global_position.getattr("x")?.extract()?;
        let global_y: f32 = global_position.getattr("y")?.extract()?;
        let global_rotation: f32 = node.getattr("global_rotation")?.extract()?;
        let texture: Vec<String> = node.getattr("texture")?.extract()?;
        let centered: bool = node.getattr("centered")?.extract()?;
        let node_transparency: Option<char> = node.getattr("transparency")?.extract()?;
        let color: Option<String> = node.getattr("color")?.extract()?;

        // Relative to screen
        let relative_x = global_x - camera_x;
        let relative_y = global_y - camera_y;

        // Texture size
        let texture_width = texture.iter().map(|row| row.len()).max().unwrap_or(0) as f32;
        let texture_height = texture.len() as f32;

        // Offset from centering
        let offset_x = if centered { texture_width / 2.0 } else { 0.0 };
        let offset_y = if centered { texture_height / 2.0 } else { 0.0 };

        // Iterate over each cell, for each row
        for (h, row) in texture.iter().enumerate() {
            for (w, cell) in row.chars().enumerate() {
                if let Some(transparency_char) = node_transparency {
                    if cell == transparency_char {
                        continue;
                    }
                }

                // Adjust starting point based on centering
                let x_diff = (w as f32) - offset_x;
                let y_diff = (h as f32) - offset_y;

                // Apply rotation using upper-left as the origin
                let rotated_x = global_rotation.cos() * x_diff - global_rotation.sin() * y_diff;
                let rotated_y = global_rotation.sin() * x_diff + global_rotation.cos() * y_diff;

                // Translate to final screen position
                let final_x = relative_x + rotated_x;
                let final_y = relative_y + rotated_y;

                // Snap to indexes
                let cell_index = final_x.floor() as i32;
                let row_index = final_y.floor() as i32;

                // Do boundary checks
                if 0 > cell_index || cell_index >= (screen_width as i32) {
                    continue;
                }
                if 0 > row_index || row_index >= (screen_height as i32) {
                    continue;
                }
                screen_buf[row_index as usize][cell_index as usize] = (cell, color.clone());
            }
        }
    }

    // Convert 2D `Vec` of `char` to `String` joined with "\n"
    let out = screen_buf
        .iter()
        .map(|line_buf| {
            line_buf
                .iter()
                .map(|(cell, color)| {
                    if let Some(color_code) = color {
                        format!("{RESET}{color_code}{cell}")
                    } else {
                        format!("{RESET}{cell}")
                    }
                })
                .collect()
        })
        .collect::<Vec<String>>()
        .join("\n");

    Ok(out)
}

// TODO: Implement flipping and rotation db

#[pymodule]
fn termnautica(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_all, m)?)?;
    Ok(())
}
