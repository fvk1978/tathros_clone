!(function() {
    var RESOURCE_PHOTOGRAPHERS = '/photographers/',
        selectedIds = [],
        page = 0,
        searchElem = $("#query_string");

    function updateCount(id, elem) {
        // TODO: make this function testable, enforce one-task per one-function principle
        var queueLength,
            selectedElemIdx = selectedIds.indexOf(id);
        if (id === null) {
            // reset all
            selectedIds = [];
        }
        else if (selectedElemIdx > -1) {
            selectedIds.splice(selectedElemIdx, 1);
        } else {
            selectedIds.push(id);
        }

        if (elem) {
            elem.toggleClass('selected');
        }

        queueLength = selectedIds.length;

        if (!queueLength) {
            $('.btn').addClass('disabled');
            $('.status').html(' ');
        } else {
            $('.btn').removeClass('disabled');
            $('.status').html('(' + queueLength + ')');
        }
    }

    function loadMoreContent (e) {
        if ($(this).hasClass('disabled')) {
            return false;
        }

        if(e.type !== 'scroll') {
            // reset everything, fresh search
            // TODO: implement via dependency injection
            window.mapRefocus();
            lastTrigger = 0;
            page = 0;
            updateCount(null);
        }

        var resource = searchElem.data('resource'),
            hiddenIds = $('input[name=hidden_ids]').map(function () {
                    return $(this).val();
                })
                    .get(),
            query = searchElem.val(),
            postData = {
                query_string: query,
                geo: {
                    range: $("input[name=search_range]:checked").val(),
                    lng: searchElem.data('lng'),
                    lat: searchElem.data('lat'),
                    name: searchElem.val()
                },
                hidden_ids:  hiddenIds,
                category: $("#category").val(),
                page: !!query ? page : 0
            };

        $.post(resource, postData, function(data) {
            var resSet = $('.result_set'),
                 $grid = $('#grid'),
                 $items = $(data),
                 total;

            if (e.type !== 'scroll') {
                //reset content if it's a fresh search. e.g. not a scroll
                resSet.html('');
               if (!!data.trim()) {
                   //show total if there is data
                   $('h4.total')
                        .removeClass('hidden')
                    $('h4.error')
                        .addClass('hidden');

                   total = $($items[0]).data('total');
                   if(total) {
                       $("#counter").html(total);
                   }
                } else {
                   //otherwise show error message - no images
                    $('h4.error')
                        .removeClass('hidden');
                    $('h4.total')
                        .addClass('hidden');
                }
            }

            // append items to grid
            $grid.append( $items )
            // add and lay out newly appended items
                .masonry( 'appended', $items );

            // reload when images are loaded
            $grid.imagesLoaded(function() {
                $grid.masonry('reloadItems');
                $grid.masonry('layout');
            });
        });
    }

    var lastTrigger = 0;
    $('body').on('mouseup', 'img',function () {
        var id = $(this).data('id');
        updateCount(id, $(this));
    } );

    $(function() {
        $("#grid").masonry({
            itemSelector: '.item',
            gutter: 15,
            columnWidth: 1,
            transitionDuration: '1s'
        });
        $(window).scroll(function() {
            //trigger at the middle of the scroll
            var triggerPoint = (lastTrigger + $(document).height()) / 2,
                currentPos = $(window).scrollTop();
            if (currentPos > triggerPoint) {
                lastTrigger = currentPos;
                page += 1;
                loadMoreContent({type: 'scroll'});
            }
        });

        //Prevent submission by enter press
        $("#searchForm").on('submit', function(e) {
            e.preventDefault();
            loadMoreContent(e);
            return false;
        });

        // Explicit search click or range change
        $('#search').on('click', loadMoreContent);
        $("input[name=search_range]:radio, #category").on('change', function (e) {
            loadMoreContent(e);
        });

        $('#results_link').on('click', function () {
            if ($(this).hasClass('disabled')) {
                return false;
            }

             var form = document.createElement('form');
            form.method = 'post';
            form.action = RESOURCE_PHOTOGRAPHERS;

            var input = document.createElement('input'),
                range = document.createElement('input'),
                lng = document.createElement('input'),
                lat = document.createElement('input');

            input.type= 'hidden';
            input.name = 'ids';
            input.value = decodeURIComponent(selectedIds);

            range.type = 'hidden';
            range.name = 'range';
            range.value = $('input[name="search_range"]:checked').data('range');

            lng.type = 'hidden';
            lng.name = 'lng';
            lng.value = searchElem.data('lng');

            lat.type = 'hidden';
            lat.name = 'lat';
            lat.value = searchElem.data('lat');

            form.appendChild(input);
            form.appendChild(range);
            form.appendChild(lng);
            form.appendChild(lat);

            document.body.appendChild(form);
            form.submit();
            return false;
        });
    });
}());
