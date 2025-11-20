# Web Structure and Element Analysis for JSI Scraper

This document analyzes the HTML structure of the sample page to identify elements needed for scraping the requested data fields.

## Data Fields to Scrape

### 1. Projek (Project)
- **Element**: Main post title
- **Selector**: `h1.wp-block-post-title a`
- **Example**: "Gangsadewa Ethnic Ensemble"
- **Path**: Located in the main content area after the header

### 2. Date Posted
- **Element**: Post date/time
- **Selector**: `div.wp-block-post-date time`
- **Example**: "Agustus 11, 2025" (August 11, 2025)
- **Format**: `datetime` attribute contains ISO format, text content contains localized format

### 3. Author
- **Element**: Post author
- **Selector**: `div.wp-block-post-author .wp-block-post-author__name`
- **Example**: "staticshelf"

### 4. Deskripsi (Description)
- **Element**: Paragraph following "Deskripsi" heading
- **Selector**: `p:contains('Deskripsi') + p` or `p:contains('Gangsadewa Ethnic Ensemble adalah projek musik eksperimental')`
- **Note**: Description appears as a paragraph after the "Deskripsi" heading in bold

### 5. Format
- **Element**: Format tags/buttons
- **Selector**: `div.wp-block-buttons:contains('Format') + div.wp-block-buttons a.wp-block-button__link`
- **Example**: "Mixed ensemble"
- **Structure**: Buttons contained within a block-buttons div

### 6. Anggota (Members)
- **Element**: Member tags/buttons
- **Selector**: `div.wp-block-buttons:contains('Anggota') + div.wp-block-buttons a.wp-block-button__link`
- **Examples**: "R. Chairul Slamet", "Dwi Heriyana", "Putri Edysud", etc.
- **Structure**: Multiple buttons within a block-buttons div

### 7. Genre
- **Element**: Genre tags/buttons
- **Selector**: `div.wp-block-buttons:contains('Genre') + div.wp-block-buttons a.wp-block-button__link`
- **Examples**: "Contemporary Classical", "Free Improvisation"
- **Structure**: Multiple buttons within a block-buttons div

### 8. Tahun (Year)
- **Element**: Year tags/buttons
- **Selector**: `div.wp-block-buttons:contains('Tahun') + div.wp-block-buttons a.wp-block-button__link`
- **Example**: "2008"
- **Structure**: Single button within a block-buttons div

### 9. Status
- **Element**: Status tags/buttons
- **Selector**: `div.wp-block-buttons:contains('Status') + div.wp-block-buttons a.wp-block-button__link`
- **Example**: "Aktif"
- **Structure**: Single button within a block-buttons div

### 10. Diskografi (Discography)
- **Element**: Table with discography data
- **Selector**: `figure.wp-block-table table`
- **Structure**: 
  - Headings: `table thead tr th`
  - Content: `table tbody tr td`
  - Columns: Tahun, Judul, Jenis, Format, Pranala terkait
- **Example**: 
  - Row 1: 2008, Mixture, Album, Digital;Compact Disc;, [1]
  - Row 2: 2015, Renungan, Single, Digital, [1]

### 11. Pranala (Links)
- **Element**: Link buttons
- **Selector**: `div.wp-block-buttons:contains('Pranala') + div.wp-block-buttons a.wp-block-button__link`
- **Examples**: Instagram, Spotify, Soundcloud
- **Structure**: Multiple buttons within a block-buttons div

### 12. Image
- **Element**: Media gallery images
- **Selector**: `figure.wp-block-gallery img` or `figure.wp-block-gallery figure.wp-block-image img`
- **Examples**:
  - `img.wp-image-7701` - JSI_Projek_Gangsadewa Ethnic Ensemble (1)
  - `img.wp-image-7700` - JSI_Projek_Gangsadewa Ethnic Ensemble (2)
  - `img.wp-image-7702` - JSI_Projek_Gangsadewa Ethnic Ensemble (3)
- **Note**: Images contained within a gallery block with captions and metadata

## HTML Structure Overview

The page follows a WordPress/WooCommerce structure with:

1. **Header Section**:
   - Site logo and navigation
   - Search functionality

2. **Main Content Area**:
   - Post title
   - Post metadata (date, author)
   - Content sections organized by headings
   - Each data field has a structured content block
   - Media gallery with images
   - Video embeds (YouTube)

3. **Footer Section**:
   - Social links
   - Site information

## Scraping Strategy

1. **Title**: Extract from `.wp-block-post-title a`
2. **Date & Author**: Extract from `.wp-block-post-date` and `.wp-block-post-author` respectively
3. **Content Fields**: For fields like format, members, genre, etc., find the heading with the label and then get the following block with buttons
4. **Description**: Extract paragraph content following the "Deskripsi" heading
5. **Discography**: Parse the table structure under the "Diskografi" heading
6. **Images**: Extract all images from the gallery block
7. **External Links**: Extract links from the "Pranala" section

## Special Considerations

- The site uses WordPress block structure, with each section contained in specific block classes
- Many elements are in button format (`wp-block-button__link`)
- Images have metadata stored in data attributes
- The discography is in a structured table format
- Dates are in both ISO and localized format