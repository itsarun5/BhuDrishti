import streamlit.components.v1 as components
import folium
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import rasterio
import folium
from rasterio.io import MemoryFile
from modules.ndvi import calculate_ndvi
from modules.ndwi import calculate_ndwi
from modules.ndbi import calculate_ndbi
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from rasterio.warp import calculate_default_transform, reproject, Resampling

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="BhuDrishti",
    page_icon="🌍",
    layout="wide"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🌍 BhuDrishti")
st.subheader("Satellite-Based Environmental Monitoring")

st.sidebar.title("BhuDrishti")
st.sidebar.markdown("Select a monitoring module")

module = st.sidebar.selectbox(
    "Select a module",
    [
        "Dashboard",
        "Crop Health Monitoring",
        "Water Monitoring",
        "Urban Monitoring",
        "Climate Monitoring"
    ]
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------


if module == "Dashboard":

    st.header("🌍 BhuDrishti Dashboard")

    st.write(
        "Satellite-Based Environmental Monitoring System"
    )

    st.markdown("---")

    st.subheader("Environmental Monitoring Overview")

    col1, col2, col3 = st.columns(3)

    ndvi_data = st.session_state.get("ndvi_results")
    ndwi_data = st.session_state.get("ndwi_results")
    ndbi_data = st.session_state.get("ndbi_results")

    with col1:
        st.markdown("### 🌱 Crop Health")
        if ndvi_data:
            st.metric(
                "Average NDVI",
                f"{ndvi_data['average']:.3f}"
            )
            st.caption("Latest vegetation analysis")
        else:
            st.info("No NDVI analysis yet")

    with col2:
        st.markdown("### 💧 Water Monitoring")
        if ndwi_data:
            st.metric(
                "Estimated Water Pixels",
                f"{ndwi_data['water_percentage']:.2f}%"
            )
            st.caption("Latest water analysis")
        else:
            st.info("No NDWI analysis yet")

    with col3:
        st.markdown("### 🏙️ Urban Monitoring")
        if ndbi_data:
            st.metric(
                "Potential Built-up Pixels",
                f"{ndbi_data['builtup_percentage']:.2f}%"
            )
            st.caption("Latest urban analysis")
        else:
            st.info("No NDBI analysis yet")

    st.markdown("---")

    st.subheader("Available Analysis Modules")

    col1, col2, col3 = st.columns(3)

    col1.info("🌱 NDVI\n\nVegetation and crop health analysis")

    col2.info("💧 NDWI\n\nWater body identification")

    col3.info("🏙️ NDBI\n\nBuilt-up area analysis")

    st.markdown("---")

    st.subheader("About BhuDrishti")

    st.write(
        "BhuDrishti uses satellite imagery and geospatial "
        "processing to analyse vegetation, water resources "
        "and urban development."
    )

    st.caption("BhuDrishti | ASTRA 2026")

    


# --------------------------------------------------
# CROP HEALTH MONITORING
# --------------------------------------------------

elif module == "Crop Health Monitoring":

    st.header("🌱 Crop Health Monitoring")

    st.write(
        "Upload matching Red and Near Infrared satellite "
        "bands from the same Resourcesat-2A LISS-III acquisition."
    )

    st.info(
        "Resourcesat-2A LISS-III band mapping: "
        "BAND3 = Red and BAND4 = Near Infrared (NIR)."
    )

    red_file = st.file_uploader(
        "Upload Red Band (Resourcesat-2A BAND3)",
        type=["tif", "tiff"],
        key="red_band"
    )

    nir_file = st.file_uploader(
        "Upload Near Infrared Band (Resourcesat-2A BAND4)",
        type=["tif", "tiff"],
        key="nir_band"
    )

    if red_file is not None and nir_file is not None:

        st.success("Both satellite bands uploaded!")

        if st.button("Calculate NDVI", type="primary") or st.session_state.get("show_results", False):
            st.session_state["show_results"] = True

            try:
                with st.spinner("Processing satellite imagery..."):

                    # Calculate full-resolution NDVI
                    ndvi, red_crs, profile = calculate_ndvi(
                        red_file,
                        nir_file
                    )

                    ndvi_array = np.ma.asarray(ndvi)

                    # Convert invalid and masked pixels to NaN
                    ndvi_array = np.ma.filled(
                        ndvi_array,
                        np.nan
                    ).astype(np.float32)

                    ndvi_array = np.squeeze(ndvi_array)

                    valid_pixels = ndvi_array[
                        np.isfinite(ndvi_array)
                    ]

                    if valid_pixels.size == 0:
                        st.error(
                            "No valid NDVI pixels were found. "
                            "Please check your satellite files."
                        )
                        st.stop()

                    # Calculate statistics using full-resolution data
                    average_ndvi = float(np.mean(valid_pixels))
                    maximum_ndvi = float(np.max(valid_pixels))
                    minimum_ndvi = float(np.min(valid_pixels))
                    st.session_state["ndvi_results"] = {
                    "average": average_ndvi,
                    "maximum": maximum_ndvi,
                    "minimum": minimum_ndvi
                    }

                st.success("NDVI calculation completed!")

                # ------------------------------------------
                # DISPLAY STATISTICS
                # ------------------------------------------

                st.subheader("NDVI Analysis Results")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Average NDVI",
                    f"{average_ndvi:.3f}"
                )

                col2.metric(
                    "Maximum NDVI",
                    f"{maximum_ndvi:.3f}"
                )

                col3.metric(
                    "Minimum NDVI",
                    f"{minimum_ndvi:.3f}"
                )

                # ------------------------------------------
                # REDUCE IMAGE SIZE FOR DISPLAY ONLY
                # ------------------------------------------

                st.subheader("Vegetation Health Map")

                height, width = ndvi_array.shape

                # Display at most approximately 700 pixels
                # along the longest dimension.
                step = max(
                    1,
                    int(np.ceil(max(height, width) / 700))
                )

                display_array = ndvi_array[
                    ::step,
                    ::step
                ]

                fig = go.Figure(
                    data=go.Heatmap(
                        z=display_array,
                        colorscale="RdYlGn",
                        zmin=-1,
                        zmax=1,
                        colorbar=dict(
                            title="NDVI"
                        ),
                        hovertemplate=(
                            "Row: %{y}<br>"
                            "Column: %{x}<br>"
                            "NDVI: %{z:.3f}"
                            "<extra></extra>"
                        )
                    )
                )

                fig.update_layout(
                    title="NDVI Vegetation Index",
                    xaxis_title="Image Columns",
                    yaxis_title="Image Rows",
                    height=600
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.caption(
                    "The displayed map is downsampled for faster "
                    "visualization. Statistics and exported data "
                    "use the full-resolution NDVI array."
                )

                # ------------------------------------------
                # NDVI INTERPRETATION
                # ------------------------------------------

                st.subheader("🌍 Geographical NDVI Map")

                # Get satellite image dimensions and geographic information
                height, width = ndvi_array.shape

                if profile["crs"] is None:
                    raise ValueError("Satellite image has no CRS information.")

                # Convert satellite coordinates into latitude and longitude
                left, bottom, right, top = rasterio.transform.array_bounds(
                    height,
                    width,
                    profile["transform"]
                )

                display_width = min(width, 700)
                display_height = max(
                    1,
                    int(height * display_width / width)
                )

                dst_transform, dst_width, dst_height = calculate_default_transform(
                    profile["crs"],
                    "EPSG:4326",
                    width,
                    height,
                    left,
                    bottom,
                    right,
                    top,
                    dst_width=display_width,
                    dst_height=display_height
                )

                # Reproject NDVI into geographical coordinates
                geographic_ndvi = np.full(
                    (dst_height, dst_width),
                    np.nan,
                    dtype=np.float32
                )

                reproject(
                    source=ndvi_array,
                    destination=geographic_ndvi,
                    src_transform=profile["transform"],
                    src_crs=profile["crs"],
                    dst_transform=dst_transform,
                    dst_crs="EPSG:4326",
                    src_nodata=np.nan,
                    dst_nodata=np.nan,
                    resampling=Resampling.nearest
                )

                # Create a coloured NDVI image
                cmap = plt.get_cmap("RdYlGn")
                normalized = np.clip(
                    (geographic_ndvi + 1) / 2,
                    0,
                    1
                )

                rgba_image = cmap(normalized)
                rgba_image[~np.isfinite(geographic_ndvi)] = [0, 0, 0, 0]

                rgba_image = (rgba_image * 255).astype(np.uint8)

                # Get geographical boundaries
                geo_bounds = rasterio.transform.array_bounds(
                    dst_height,
                    dst_width,
                    dst_transform
                )

                west, south, east, north = geo_bounds

                # Create interactive map
                center_lat = (south + north) / 2
                center_lon = (west + east) / 2

                ndvi_map = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=9,
                    tiles="OpenStreetMap"
                )

                # Add NDVI satellite layer
                folium.raster_layers.ImageOverlay(
                    image=rgba_image,
                    bounds=[[south, west], [north, east]],
                    opacity=0.75,
                    name="NDVI Vegetation Layer",
                    interactive=True
                ).add_to(ndvi_map)

                folium.LayerControl().add_to(ndvi_map)

                # Display map in Streamlit
                components.html(
                   ndvi_map.get_root().render(),
                   height=650,
                   scrolling=False
)


                st.caption(
                    "NDVI overlay displayed using geographical coordinates. "
                    "The visualization is downsampled; original NDVI data "
                    "is retained for calculations and export."
                )

                # ------------------------------------------
                # DOWNLOAD FULL-RESOLUTION NDVI GEOTIFF
                # ------------------------------------------

                st.subheader("Download Satellite Analysis")

                nodata_value = -9999.0

                output_array = np.where(
                    np.isfinite(ndvi_array),
                    ndvi_array,
                    nodata_value
                ).astype(np.float32)

                output_profile = profile.copy()

                output_profile.update(
                    driver="GTiff",
                    count=1,
                    dtype="float32",
                    nodata=nodata_value,
                    compress="deflate"
                )

                # Write the complete NDVI image to GeoTIFF
                with MemoryFile() as memory_file:

                    with memory_file.open(
                        **output_profile
                    ) as dataset:

                        dataset.write(
                            output_array,
                            1
                        )

                    ndvi_tiff = memory_file.read()

                st.download_button(
                    label="Download Full-Resolution NDVI GeoTIFF",
                    data=ndvi_tiff,
                    file_name="BhuDrishti_NDVI.tif",
                    mime="image/tiff"
                )

            except Exception as error:

                st.error(
                    f"NDVI processing failed: {error}"
                )

                st.info(
                    "Check that both files belong to the "
                    "same satellite acquisition and have "
                    "matching dimensions and coordinates."
                )


# --------------------------------------------------
# WATER MONITORING
# --------------------------------------------------


elif module == "Water Monitoring":

    st.header("💧 Water Monitoring")

    st.write(
        "Identify and analyse water bodies using satellite imagery "
        "and the Normalized Difference Water Index (NDWI)."
    )

    st.info(
        "Resourcesat-2A LISS-III: BAND2 = Green and BAND4 = NIR."
    )

    green_file = st.file_uploader(
        "Upload Green Band (BAND2)",
        type=["tif", "tiff"],
        key="green_band"
    )

    nir_water_file = st.file_uploader(
        "Upload Near Infrared Band (BAND4)",
        type=["tif", "tiff"],
        key="water_nir_band"
    )

    if green_file is not None and nir_water_file is not None:

        st.success("Both satellite bands uploaded!")

        if st.button("Calculate NDWI", type="primary"):

            try:
                with st.spinner("Analysing water bodies..."):

                    ndwi, water_crs, water_profile = calculate_ndwi(
                        green_file,
                        nir_water_file
                    )

                    ndwi = np.asarray(ndwi, dtype=np.float32)

                    valid_pixels = ndwi[np.isfinite(ndwi)]

                    if valid_pixels.size == 0:
                        st.error("No valid NDWI pixels found.")
                        st.stop()

                    average_ndwi = float(np.mean(valid_pixels))

                    # Initial water estimate: NDWI greater than 0
                    water_pixels = valid_pixels[valid_pixels > 0]

                    water_percentage = (
                        len(water_pixels) / len(valid_pixels)
                    ) * 100

                    st.session_state["ndwi_results"] = {
                       "array": ndwi,
                       "average": average_ndwi,
                       "water_percentage": water_percentage,
                       "profile": water_profile
                    }

            except Exception as error:
                st.error(f"NDWI processing failed: {error}")

    if "ndwi_results" in st.session_state:

        results = st.session_state["ndwi_results"]

        st.subheader("Water Analysis Results")

        col1, col2 = st.columns(2)

        col1.metric(
            "Average NDWI",
            f"{results['average']:.3f}"
        )

        col2.metric(
            "Estimated Water Pixels",
            f"{results['water_percentage']:.2f}%"
        )

        st.subheader("Water Detection Map")

        ndwi_array = results["array"]

        height, width = ndwi_array.shape

        step = max(1, int(np.ceil(max(height, width) / 700)))

        display_array = ndwi_array[::step, ::step]

        fig = go.Figure(
            data=go.Heatmap(
                z=display_array,
                colorscale="Blues",
                zmin=-1,
                zmax=1,
                colorbar=dict(title="NDWI")
            )
        )

        fig.update_layout(
            title="NDWI Water Index",
            xaxis_title="Image Columns",
            yaxis_title="Image Rows",
            height=600
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Geographical Water Detection Map")

        profile = results["profile"]

        if profile["crs"] is None:
            st.error("Satellite image has no CRS information.")
        else:
            height, width = ndwi_array.shape

            left, bottom, right, top = rasterio.transform.array_bounds(
                height,
                width,
                profile["transform"]
            )

            display_width = min(width, 700)
            display_height = max(
                1,
                int(height * display_width / width)
            )

            dst_transform, dst_width, dst_height = calculate_default_transform(
                profile["crs"],
                "EPSG:4326",
                width,
                height,
                left,
                bottom,
                right,
                top,
                dst_width=display_width,
                dst_height=display_height
            )

            geographic_ndwi = np.full(
                (dst_height, dst_width),
                np.nan,
                dtype=np.float32
            )

            reproject(
                source=ndwi_array,
                destination=geographic_ndwi,
                src_transform=profile["transform"],
                src_crs=profile["crs"],
                dst_transform=dst_transform,
                dst_crs="EPSG:4326",
                src_nodata=np.nan,
                dst_nodata=np.nan,
                resampling=Resampling.nearest
            )

            # Highlight potential water pixels in blue
            rgba_image = np.zeros(
                (dst_height, dst_width, 4),
                dtype=np.uint8
            )

            water_mask = (
                np.isfinite(geographic_ndwi) &
                (geographic_ndwi > 0)
            )

            rgba_image[water_mask] = [0, 100, 255, 180]

            west, south, east, north = rasterio.transform.array_bounds(
                dst_height,
                dst_width,
                dst_transform
            )

            center_lat = (south + north) / 2
            center_lon = (west + east) / 2

            water_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=9,
                tiles="OpenStreetMap"
            )

            folium.raster_layers.ImageOverlay(
                image=rgba_image,
                bounds=[[south, west], [north, east]],
                opacity=0.8,
                name="Potential Water Bodies"
            ).add_to(water_map)

            folium.LayerControl().add_to(water_map)

            components.html(
                water_map.get_root().render(),
                height=650,
                scrolling=False
            )


        st.caption(
            "Positive NDWI pixels are treated as potential water pixels "
            "using an initial threshold of 0.0. This is an estimate, "
            "not a confirmed water classification."
        )



# --------------------------------------------------
# URBAN MONITORING
# --------------------------------------------------


elif module == "Urban Monitoring":

    st.header("🏙️ Urban Monitoring")

    st.write(
        "Analyse built-up areas and identify potential urban "
        "development using satellite imagery."
    )

    st.info(
        "Resourcesat-2A LISS-III: BAND5 = SWIR and BAND4 = NIR."
    )

    swir_file = st.file_uploader(
        "Upload Shortwave Infrared Band (BAND5)",
        type=["tif", "tiff"],
        key="swir_band"
    )

    nir_urban_file = st.file_uploader(
        "Upload Near Infrared Band (BAND4)",
        type=["tif", "tiff"],
        key="urban_nir_band"
    )

    if swir_file is not None and nir_urban_file is not None:

        st.success("Both satellite bands uploaded!")

        if st.button("Calculate NDBI", type="primary"):

            try:
                with st.spinner("Analysing urban areas..."):

                    ndbi, urban_crs, urban_profile = calculate_ndbi(
                        swir_file,
                        nir_urban_file
                    )

                    ndbi = np.asarray(ndbi, dtype=np.float32)

                    valid_pixels = ndbi[np.isfinite(ndbi)]

                    if valid_pixels.size == 0:
                        st.error("No valid NDBI pixels found.")
                        st.stop()

                    average_ndbi = float(np.mean(valid_pixels))

                    # Initial estimate of potential built-up pixels
                    builtup_pixels = valid_pixels[valid_pixels > 0]

                    builtup_percentage = (
                        len(builtup_pixels) / len(valid_pixels)
                    ) * 100

                    st.session_state["ndbi_results"] = {
                        "array": ndbi,
                        "average": average_ndbi,
                        "builtup_percentage": builtup_percentage
                    }

            except Exception as error:
                st.error(f"NDBI processing failed: {error}")

    if "ndbi_results" in st.session_state:

        results = st.session_state["ndbi_results"]

        st.subheader("Urban Analysis Results")

        col1, col2 = st.columns(2)

        col1.metric(
            "Average NDBI",
            f"{results['average']:.3f}"
        )

        col2.metric(
            "Potential Built-up Pixels",
            f"{results['builtup_percentage']:.2f}%"
        )

        st.subheader("Built-up Area Detection Map")

        ndbi_array = results["array"]

        height, width = ndbi_array.shape

        step = max(1, int(np.ceil(max(height, width) / 700)))

        display_array = ndbi_array[::step, ::step]

        fig = go.Figure(
            data=go.Heatmap(
                z=display_array,
                colorscale="RdYlBu_r",
                zmin=-1,
                zmax=1,
                colorbar=dict(title="NDBI")
            )
        )

        fig.update_layout(
            title="NDBI Built-up Index",
            xaxis_title="Image Columns",
            yaxis_title="Image Rows",
            height=600
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Pixels with NDBI greater than 0 are marked as potential "
            "built-up pixels. Bare soil and other surfaces may also "
            "produce positive values, so this is an initial estimate."
        )

    


# --------------------------------------------------
# CLIMATE MONITORING
# --------------------------------------------------

elif module == "Climate Monitoring":

    st.header("🌦️ Climate Monitoring")

    st.info(
        "Climate monitoring features will be implemented here."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.caption("BhuDrishti | ASTRA 2026")
