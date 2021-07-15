# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/v_tools/

import bmesh
import bpy
from mathutils import Vector


class VTools:

    @classmethod
    def loop_resolve(cls, context, STEP, dist):
        # Resolve loop density by Bezier in vertex mode or split edges in edges mode
        def getTBSegment(segment, Pc, T, R, D):
            kk = (1 - T) * 0.5
            t = kk + T
            k_extr = 0
            b = Vector()
            for cycle in range(100):
                segment.calc(t, b)
                d_ = (b - Pc).length - R

                if abs(d_) <= D: return (t, b)

                if kk == k_extr:
                    k = -0.5 if d_ > 0 else 0.5
                else:
                    k = -1 if d_ > 0 else 1
                    k_extr = kk

                kk *= k
                t += kk
                kk = abs(kk)
            return (t, b)

        cls.edit_mode_out()
        cls.edit_mode_in()

        obj = context.active_object
        me = obj.data

        verts = cls.find_index_of_selected_vertex(me)

        segments_2d = cls.find_all_segments(me, 3)
        if not segments_2d: return False
        # Запускаем 2д-перестроение по сплайну
        cls.edit_mode_out()
        bm = bmesh.new()
        bm.from_mesh(me)
        cls.check_lukap(bm)
        cls.edit_mode_in()

        lv_for_del = []
        old_len_lfd = 0
        old_len_bmv = 0
        bm_verts = []
        remove_edges = []
        set_verts = set(verts)
        act_vert = cls.bm_vert_active_get(bm)[0]
        for i, sort_list_ in enumerate(segments_2d):
            _is_loop = False
            if len(sort_list_) == 2:
                extreme_vs = sort_list_
            else:
                extreme_vs = cls.find_extreme_select_verts(me, sort_list_)
                if not extreme_vs:
                    _is_loop = True
                    _loc_idx = sort_list_.index(act_vert)
                    _sort_list_ = sort_list_[_loc_idx:] + sort_list_[:_loc_idx]
                    sort_list_ = _sort_list_

                    len_sort_list_ = len(sort_list_)
                    _sub_segment_1 = sort_list_[:len_sort_list_ // 2 + 1]
                    _sub_segment_2 = sort_list_[len_sort_list_ // 2:] + [sort_list_[0]]
                    segments_2d[i] = _sub_segment_1
                    segments_2d.insert(i + 1, _sub_segment_2)
                    sort_list_ = _sub_segment_1
                    if len(sort_list_) == 2:
                        extreme_vs = sort_list_
                    else:
                        extreme_vs = cls.find_extreme_select_verts(me, sort_list_)

            if _is_loop:
                sort_list = sort_list_
            else:
                bl_ = list(set(sort_list_) ^ set_verts)
                sort_list = cls.find_all_connected_verts(me, extreme_vs[0], bl_)

            list_length = []
            sum_length = 0.0
            cou_vs = len(sort_list) - 1
            list_koeff = []
            if cou_vs == 1:
                p1co = me.vertices[sort_list[0]].co.copy()
                p3co = me.vertices[sort_list[1]].co.copy()
                p2co = (p1co + p3co) / 2
                sum_length = (p3co - p1co).length
                # list_length = [sum_length / 2, sum_length]
                list_koeff = [0.5, 0.5]
                values = [p1co, p2co, p3co]
            else:
                for sl in range(cou_vs):
                    subb = me.vertices[sort_list[sl + 1]].co - me.vertices[sort_list[sl]].co
                    sum_length += subb.length
                    list_length.append(subb.length)

                for sl in range(cou_vs):
                    tmp = list_length[sl] / sum_length
                    list_koeff.append(tmp)

                values = [me.vertices[i].co.copy() for i in sort_list]

            n = len(values) - 1
            bezier = [Segment() for _ in range(n)]

            step_ = STEP - 1
            new_vts = []

            if not dist:
                r = sum_length / (step_)
            else:
                r = dist
                step_ = 1e+6

            pi_ = 0
            delta = 0.001
            for i in range(n):
                if i == n - 1: pi_ = 1

                tl = list_koeff[i - pi_]
                tr = list_koeff[i + 1 - pi_]
                tt = tl / (tl + tr)

                bezier[i].points[0] = values[i - pi_]
                b = values[i + 1 - pi_]
                bezier[i].points[2] = values[i + 2 - pi_]
                bezier[i].calc_p1(tt, b)
                bezier[i].points[3] = b

            for j in range(4):
                segment = bezier[0]
                Pc = segment.points[0].copy()
                t = 0
                i = 0
                ii = 0
                iii = 0
                pi_ = 0
                i_virtual = 0
                dr = 0
                old_point = me.vertices[extreme_vs[0]].co.copy()
                while i < len(bezier):
                    ii += 1
                    segment = bezier[i]
                    if i == len(bezier) - 1: pi_ = 1

                    if (Pc - segment.points[3 - pi_]).length < r:
                        t = 0 if i < len(bezier) - 2 else t
                        i += 1
                        if i_virtual < step_: i_virtual += 1
                        if i == len(bezier) and j == 3:
                            t, b = getTBSegment(segment, Pc, t, r, delta)
                            if len(new_vts) < step_: new_vts.append(b.copy())
                        continue

                    t, b = getTBSegment(segment, Pc, t, r, delta)
                    Pc = b
                    if i_virtual < step_ + 1:
                        # Pc1 = Pc.copy()
                        i_virtual += 1

                    if j == 3:
                        if len(new_vts) < step_: new_vts.append(b.copy())

                    iii += 1
                    dr += (old_point - Pc).length
                    old_point = Pc.copy()

                r = dr / iii
                if dist:
                    r = dist

            new_vts.insert(0, me.vertices[extreme_vs[0]].co)

            # В списке new_vts имеем координаты новых вершин
            cls.edit_mode_out()
            lv_for_del.extend([bm.verts[vi] for vi in sort_list])
            for v in new_vts[1:-1]:
                new_v = bm.verts.new(v)
                new_v.select = True
                bm_verts.append(new_v)

            cls.check_lukap(bm)

            v0_insert = lv_for_del.pop(old_len_lfd)
            v1_insert = lv_for_del.pop(-1)
            if len(sort_list) == 2:
                edge = bm.edges.get([v0_insert, v1_insert], False)
                if edge: remove_edges.append(edge)

            bm_verts.insert(old_len_bmv, v0_insert)
            bm_verts.append(v1_insert)
            bm_verts[old_len_bmv].select = True
            bm_verts[-1].select = True
            bm_edges = list(zip(bm_verts[old_len_bmv:-1], bm_verts[1 + old_len_bmv:]))
            old_len_lfd = len(lv_for_del)
            old_len_bmv = len(bm_verts)

            for edge in bm_edges:
                if not bm.edges.get(edge, False):
                    ed_ = bm.edges.new(edge)
                    ed_.select = True
                else:
                    for i, re in enumerate(remove_edges):
                        if edge[0] in re.verts and edge[1] in re.verts:
                            remove_edges.pop(i)
                            break

        cls.check_lukap(bm)
        for e in remove_edges:
            bm.edges.remove(e)

        for v in lv_for_del:
            if v in bm.verts:
                bm.verts.remove(v)

        cls.check_lukap(bm)
        bm.to_mesh(me)
        bm.free()
        cls.edit_mode_in()
        return True

    @staticmethod
    def edit_mode_out():
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def edit_mode_in():
        bpy.ops.object.mode_set(mode='EDIT')

    @staticmethod
    def find_index_of_selected_vertex(mesh):
        selected_verts = [i.index for i in mesh.vertices if i.select]
        verts_selected = len(selected_verts)
        if verts_selected < 1:
            return None
        else:
            return selected_verts

    @classmethod
    def find_all_segments(cls, me, min_vts=3):
        # out: [[segment1], [segment2], ...]
        # editmode: VERTS
        edit_mode_vert = bpy.context.tool_settings.mesh_select_mode[0]
        edit_mode_edge = bpy.context.tool_settings.mesh_select_mode[1]
        if edit_mode_vert:
            # vertices = me.vertices
            l_sel_vi = cls.find_index_of_selected_vertex(me)
            if not l_sel_vi: return False
            # avi = l_sel_vi[0]
            tmp_idx_vts = l_sel_vi.copy()
            segments = []
            upp = 100  # ограничение количества сегментов
            bl = []
            set_sel_vi = set(l_sel_vi)
            while tmp_idx_vts and upp > 0:
                upp -= 1
                act_vi = tmp_idx_vts[0]
                segment = cls.find_all_connected_verts(me, act_vi, bl, 0)
                if len(segment) >= min_vts: segments.append(segment)
                tmp_idx_vts = list(set_sel_vi ^ set(bl))

            if upp < 1: return False

        elif edit_mode_edge:
            l_sel_edgs = [e for e in me.edges if e.select]
            if not l_sel_edgs: return False
            segments = []
            for e in l_sel_edgs:
                segment = [e.vertices[0], e.vertices[1]]
                segments.append(segment)

        else:
            return False

        return segments

    @staticmethod
    def find_connected_verts(me, found_index, not_list):
        edges = me.edges
        connecting_edges = [i for i in edges if found_index in i.vertices[:]]
        if len(connecting_edges) == 0:
            return []
        else:
            connected_verts = []
            for edge in connecting_edges:
                cvert = set(edge.vertices[:])
                cvert.remove(found_index)
                vert = cvert.pop()
                if not (vert in not_list) and me.vertices[vert].select:
                    connected_verts.append(vert)
            return connected_verts

    @classmethod
    def find_all_connected_verts(cls, me, active_v, not_list=[], step=0):
        vlist = [active_v]
        not_list.append(active_v)
        step += 1
        list_v_1 = cls.find_connected_verts(me, active_v, not_list)

        for v in list_v_1:
            list_v_2 = cls.find_all_connected_verts(me, v, not_list, step)
            vlist += list_v_2
        return vlist

    @staticmethod
    def check_lukap(bm):
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

    @staticmethod
    def bm_vert_active_get(bm):
        for elem in reversed(bm.select_history):
            if isinstance(elem, (bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace)):
                return elem.index, str(elem)[3:4]
        return None, None

    @staticmethod
    def find_extreme_select_verts(mesh, verts_idx):
        res_vs = []
        edges = mesh.edges

        for v_idx in verts_idx:
            connecting_edges = [i for i in edges if v_idx in i.vertices[:] and i.select \
                                and i.vertices[0] in verts_idx and i.vertices[1] in verts_idx]
            if len(connecting_edges) == 1:
                res_vs.append(v_idx)
        return res_vs


class Segment():
    def __init__(self):
        self.points = [Vector() for i in range(4)]

    def calc_p1(self, t, b):
        if t == 0: t = 1e-6
        if t == 1: t -= 1e-6

        nt = 1 - t
        nt2 = nt * nt
        t2 = t * t

        p = Vector()
        p.x = (b.x - nt2 * self.points[0].x - t2 * self.points[2].x) / (2 * t * nt)
        p.y = (b.y - nt2 * self.points[0].y - t2 * self.points[2].y) / (2 * t * nt)
        p.z = (b.z - nt2 * self.points[0].z - t2 * self.points[2].z) / (2 * t * nt)
        self.points[1] = p

    def calc(self, t, b):
        nt = 1 - t
        nt2 = nt * nt
        t2 = t * t

        b.x = nt2 * self.points[0].x + 2 * t * nt * self.points[1].x + t2 * self.points[2].x
        b.y = nt2 * self.points[0].y + 2 * t * nt * self.points[1].y + t2 * self.points[2].y
        b.z = nt2 * self.points[0].z + 2 * t * nt * self.points[1].z + t2 * self.points[2].z
